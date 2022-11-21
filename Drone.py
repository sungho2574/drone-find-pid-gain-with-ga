from vpython import *
from time import sleep

from model import Model
from mass import MassMap

import numpy as np




class Drone:
    DELAY = 0.1
    SPEED = 0.001

    def __init__(self, model_path='model/mavic.obj', dm_path='mass/test.csv') -> None:
        self.model = Model(model_path)
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
       
        self.g = 9.8 * Drone.SPEED

        self.visible = True
        self.use_double_pid = True
        self.delay = False
    

    def time_step (self):
        self.gravity()
        self.motor()

        if self.visible:
            self.model.pos(self.pos)
            self.model.ang(self.roll.ang, self.pitch.ang, self.yaw.ang)

        if self.delay:
            sleep(Drone.DELAY)
    

    def gravity (self):
        F = vec(0, - self.m * self.g, 0)
        self.translational_motion(F)

        drone_perspective_F = self.rotation_matrix(F, reverse=True)
        split = self.mass_map.m_qdrn[1:] / sum(self.mass_map.m_qdrn)
        splited_F = [s*drone_perspective_F for s in split]
        splited_F_size = list(map(mag, splited_F))
        self.rotational_motion(splited_F_size)

    
    def motor (self):
        if self.use_double_pid:
            roll_mv  = self.roll.double_pid_control(self.target_roll)
            pitch_mv = self.pitch.double_pid_control(self.target_pitch)
            yaw_mv   = self.yaw.double_pid_control(self.target_yaw)
        else:
            roll_mv  = self.roll.pid_control(self.target_roll)
            pitch_mv = self.pitch.pid_control(self.target_pitch)
            yaw_mv   = self.yaw.pid_control(self.target_yaw)

        m1 =   roll_mv - pitch_mv + yaw_mv
        m2 = - roll_mv - pitch_mv - yaw_mv
        m3 = - roll_mv + pitch_mv + yaw_mv
        m4 =   roll_mv + pitch_mv - yaw_mv

        motors = [m1, m2, m3, m4]
        drone_perspective_F = vec(0, 0, sum(motors))
        F = self.rotation_matrix(drone_perspective_F)
        self.translational_motion(F)
        self.rotational_motion(motors)


    def setTarget (self, target_roll, target_pitch, target_yaw):
        self.target_roll  = target_roll
        self.target_pitch = target_pitch
        self.target_yaw   = target_yaw


    def translational_motion(self, F):
        # forced: a to v
        a = F / self.m
        self.v += a

        # 1 second has passed: v to s
        self.pos    += self.v
        self.cg_pos += self.v
    

    def rotation_matrix (self, F: vec, reverse=False):
        # vpython coordinate system and rotation matrix coordinate system is different
        # vpython(x, y, z) = rotation_matrix(z, y, x)
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
        F = np.array([F.z, F.y, F.x]).reshape([3, 1])

        rotated_F = ROLL@PITCH@YAW@F
        return vec(rotated_F[2][0], rotated_F[1][0], rotated_F[0][0])


    def rotational_motion(self, F: list):
        # forced: alpha -> w
        Q1, Q2, Q3, Q4 = 0, 1, 2, 3
        self.roll.w   += ( (F[Q2] + F[Q3]) - (F[Q1] + F[Q4]) ) / self.mass_map.I
        self.pitch.w  += ( (F[Q1] + F[Q2]) - (F[Q3] + F[Q4]) ) / self.mass_map.I

        # 1 second has passed: w -> theta
        # An object forced in space rotates around the center of gravity.
        # But I can only control the object by center of object.
        # So the displacement of the center point shall be corrected.
        self.roll.ang  += self.roll.w
        self.pitch.ang += self.pitch.w

        r, p = self.roll.ang, self.pitch.ang
        cg_to_c = self.pos.x - self.cg_pos.x
        self.pos = self.cg_pos + vec(cg_to_c * cos(r), cg_to_c * sin(r), 0)

        cg_to_c = self.pos.z - self.cg_pos.z
        self.pos = self.cg_pos + vec(0, cg_to_c * sin(p), cg_to_c * cos(p))



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

            self.K = self.K()

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
            def __init__(self, K: list = [0, 0, 0]) -> None:
                self.setK(K)

            def setK (self, K: list):
                self.p = K[0]
                self.i = K[1]
                self.d = K[2]





if __name__ == "__main__":
    scene.width, scene.height = 800, 600

    drone = Drone()
    drone.delay = True
    
    while True:
        drone.time_step()