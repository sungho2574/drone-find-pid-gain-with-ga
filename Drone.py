from vpython import *
from model import Model
from mass import MassMap

import numpy as np



class Drone:
    TIME_STEP = 0.001

    def __init__(self, model_path='model/mavic.obj', dm_path='mass/test.csv', model_visible=True, graph_visible=True) -> None:
        # options
        self.MODEL_VISIBLE = model_visible
        self.USE_DOUBLE_PID = False

        self.LOCK_ROLL = False
        self.LOCK_PITCH = False
        
        self.LOCK_POS = False
        self.LOCK_HORIZON = False
        self.LOCK_THRUST = False

        self.GRAPH_VISIBLE = graph_visible
        if self.GRAPH_VISIBLE:
            self.graph = self.Graph()
        
        # set bacis property and physical quantity
        self.model = Model(model_path, visible=model_visible)
        self.mass_map = MassMap(dm_path)

        self.m = self.mass_map.M
        self.cg_pos = self.mass_map.cg_pos
        self.pos = vec(0, 0, 0)
        self.v   = vec(0, 0, 0)

        self.roll  = self.Axis()
        self.pitch = self.Axis()
        self.yaw   = self.Axis()

        self.target_roll  = 0
        self.target_pitch = 0
        self.target_yaw   = 0
       
        self.g = 9.8 * Drone.TIME_STEP

        #test_value
        self.USE_DOUBLE_PID = False
        self.roll.ang_control.K.setK([0.001, 0, 0])
        self.pitch.ang_control.K.setK([0.001, 0, 0])
        self.thrust_pid = self.PID([0.01, 0, 0])
    

    def time_step (self):
        self.gravity()
        self.motor()
        self.lock()

        if self.GRAPH_VISIBLE:
            self.graph.plot(self.roll.ang, self.pitch.ang, self.yaw.ang)
        
        if self.MODEL_VISIBLE:
            self.model.pos(self.pos)
            self.model.ang(self.roll.ang, self.pitch.ang, self.yaw.ang)
        
    
    def lock (self):
        if self.LOCK_ROLL:
            self.roll.ang = 0
            self.roll.w = 0
        
        if self.LOCK_PITCH:
            self.pitch.ang = 0
            self.pitch.w = 0
        
        if self.LOCK_POS:
            self.cg_pos = vec(0, 0, 0)
            self.v = vec(0, 0, 0)
        
        if self.LOCK_HORIZON:
            self.cg_pos.x = 0
            self.cg_pos.z = 0

            self.v.x = 0
            self.v.z = 0


    def gravity (self):
        F = vec(0, - self.m * self.g, 0)
        self.translational_motion(F)

        drone_perspective_F = self.rotation_matrix(F)
        split = self.mass_map.m_qdrn[1:] / sum(self.mass_map.m_qdrn)
        splited_F = [s*drone_perspective_F for s in split]
        splited_F_size = list(map(lambda f: -mag(f), splited_F))
        self.rotational_motion(splited_F_size)

    
    def motor (self):
        if self.LOCK_THRUST:
            thrust = 0
        else:
            e = 0 - self.pos.y
            thrust = self.thrust_pid.pid(e)
        
        if self.USE_DOUBLE_PID:
            roll_mv  = self.roll.double_pid_control(self.target_roll)
            pitch_mv = self.pitch.double_pid_control(self.target_pitch)
            yaw_mv   = self.yaw.double_pid_control(self.target_yaw)
        else:
            roll_mv  = self.roll.pid_control(self.target_roll)
            pitch_mv = self.pitch.pid_control(self.target_pitch)
            yaw_mv   = self.yaw.pid_control(self.target_yaw)

        m1 =   roll_mv - pitch_mv + yaw_mv + thrust
        m2 = - roll_mv - pitch_mv - yaw_mv + thrust
        m3 = - roll_mv + pitch_mv + yaw_mv + thrust
        m4 =   roll_mv + pitch_mv - yaw_mv + thrust

        motors = [m1, m2, m3, m4]
        drone_perspective_F = vec(0, sum(motors), 0)
        F = self.rotation_matrix(drone_perspective_F, reverse=True)
        self.translational_motion(F)
        self.rotational_motion(motors)


    def translational_motion(self, F):
        # forced: a to v
        a = F / self.m
        self.v += a

        # 1 second has passed: v to s
        self.pos    += self.v
        self.cg_pos += self.v
    

    def rotation_matrix (self, F: vec, reverse=False):
        # input:  the groud coordinate system
        # output: the body coordinate system
        # 지면좌표계로 측정한 힘이, 기울어진 동체좌표계 기준으로 어떻게 측정되는지 변환

        r, p, y = self.roll.ang, self.pitch.ang, self.yaw.ang
        if reverse:
            r, p, y = -r, -p, -y

        ROLL = np.array([
            1,       0,       0,
            0,  cos(r),  sin(r),
            0, -sin(r),  cos(r)

        ]).reshape([3, 3])
        PITCH = np.array([
            cos(p), 0, -sin(p),
            0,      1,       0,
            sin(p), 0,  cos(p)

        ]).reshape([3, 3])
        YAW = np.array([
                cos(y), sin(y), 0,
            -sin(y), cos(y), 0,
            0,            0, 1

        ]).reshape([3, 3])

        # vpython coordinate system and rotation matrix coordinate system is different
        # rotation_matrix(x, y, z) = vpython(z, x, y)
        F = np.array([F.z, F.x, F.y]).reshape([3, 1])

        rotated_F = ROLL@PITCH@YAW@F
        rotated_F = vec(rotated_F[0][0], rotated_F[1][0], rotated_F[2][0])
        return vec(rotated_F.y, rotated_F.z, rotated_F.x)


    def rotational_motion(self, F: list):
        # forced: alpha -> w
        Q1, Q2, Q3, Q4 = 0, 1, 2, 3
        self.roll.w   += ( (F[Q1] + F[Q4]) - (F[Q2] + F[Q3]) ) / self.mass_map.I
        self.pitch.w  += ( (F[Q3] + F[Q4]) - (F[Q1] + F[Q2]) ) / self.mass_map.I

        # 1 second has passed: w -> theta
        self.roll.ang  += self.roll.w
        self.pitch.ang += self.pitch.w

        # An object forced in space rotates around the center of gravity.
        # But I can only control the object by center of object.
        # So the displacement of the center point shall be corrected.
        r, p = self.roll.ang, self.pitch.ang
        cg_to_c = self.pos.x - self.cg_pos.x
        self.pos = self.cg_pos + vec(cg_to_c * cos(r), cg_to_c * sin(r), 0)

        cg_to_c = self.pos.z - self.cg_pos.z
        self.pos = self.cg_pos + vec(0, cg_to_c * sin(p), cg_to_c * cos(p))
    

    def clear_graph (self):
        self.graph.clear()

    def reset_physical_quantity (self):
        self.cg_pos = self.mass_map.cg_pos
        self.pos = vec(0, 0, 0)
        self.v   = vec(0, 0, 0)

        self.roll.ang = 0
        self.pitch.ang = 0
        self.yaw.ang = 0

        self.roll.w = 0
        self.pitch.w = 0
        self.yaw.w = 0

    def setAng (self, roll, pitch, yaw):                                # radians
        self.roll.ang = roll
        self.pitch.ang = pitch
        self.yaw.ang = yaw

    def setTarget (self, target_roll, target_pitch, target_yaw):        # radians
        self.target_roll  = target_roll
        self.target_pitch = target_pitch
        self.target_yaw   = target_yaw
    
    def setK (self, gain_table: list):                                  # shape = (6, 3)
        gain_table = np.array(gain_table)
        self.roll.ang_control.K.setK(gain_table[  0,  :3])
        self.pitch.ang_control.K.setK(gain_table[ 1,  :3])
        self.yaw.ang_control.K.setK(gain_table[   2,  :3])
        self.roll.w_control.K.setK(gain_table[    0, 3:6])
        self.pitch.w_control.K.setK(gain_table[   1, 3:6])
        self.yaw.w_control.K.setK(gain_table[     2, 3:6])
    
    def setDoublePID (self, b):
        self.USE_DOUBLE_PID = b
    
    def setLockRoll (self, b):
        self.LOCK_ROLL = b

    def setLockPITCH (self, b):
        self.LOCK_PITCH = b

    def setLockYaw (self, b):
        self.LOCK_YAW = b
    
    def setLockPos (self, b):
        self.LOCK_POS = b

    def setLockHorizon (self, b):
        self.LOCK_HORIZON = b

    def setLockThrust (self, b):
        self.LOCK_THRUST = b
    


    class Axis:
        def __init__(self, K_out=None, K_in=None) -> None:
            self.ang = 0
            self.w = 0

            self.ang_control = Drone.PID(K_out)
            self.w_control   = Drone.PID(K_in)

        def pid_control (self, target_ang):
            e = target_ang - self.ang
            return self.ang_control.pid(e)
        
        def double_pid_control (self, target_ang):
            target_w =  self.pid_control(target_ang)

            e = target_w - self.w
            return self.w_control.pid(e)



    class PID:
        def __init__(self, K=None) -> None:
            self.e_sum = 0              # for i control
            self.before_e = None        # for d control

            self.K = self.K(K)

        def pid (self, e):
            K = self.K
            return K.p * e  +  K.i * self.integrate(e)  +  K.d * self.diff(e)
        
        def integrate (self, e):
            self.e_sum += e
            return self.e_sum

        def diff (self, e):
            if self.before_e is None:       # first time, it should be ignored
                return 0
            else:
                diff = e - self.before_e
                self.before_e = e
                return diff


        class K:
            def __init__(self, K: list = None) -> None:
                if K is None:
                    self.setK([0, 0, 0])
                else:
                    self.setK(K)

            def setK (self, K: list):
                self.p = K[0]
                self.i = K[1]
                self.d = K[2]
    


    class Graph:
        def __init__(self) -> None:
            self.f1 = graph(align='right', width=600, height=180, title='roll')
            self.roll = gcurve(graph=self.f1, color=color.red)
            self.roll.plot(0, 0)

            self.f2 = graph(align='right', width=600, height=180, title='pitch')
            self.pitch = gcurve(graph=self.f2, color=color.red)
            self.pitch.plot(0, 0)

            self.f3 = graph(align='right', width=600, height=180, title='yaw')
            self.yaw = gcurve(graph=self.f3, color=color.red)
            self.yaw.plot(0, 0)

            self.t = 0
        
        def plot (self, roll, pitch, yaw):
            self.t += 1
            self.roll.plot(self.t, degrees(roll))
            self.pitch.plot(self.t, degrees(pitch))
            self.yaw.plot(self.t, degrees(yaw))
        
        def clear (self):
            self.roll.delete()
            self.pitch.delete()
            self.yaw.delete()
            self.t = 0




if __name__ == "__main__":
    scene.align = 'left'
    scene.width, scene.height = 1050, 800

    drone = Drone()
    drone.setLockPos(True)

    while True:
        sleep(0.1)
        drone.time_step()