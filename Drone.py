from vpython import *
from model import Model
from mass import MassMap

import numpy as np

class Drone:

    def __init__(self, model_path, dm_path) -> None: 
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
       
        self.g = 9.8

        self.visible = True
        self.use_double_pid = True
    

    def time_step (self):
        self.gravity()
        self.motor()

        if self.visible:
            self.model.pos(self.pos)
            self.model.ang(self.roll, self.pitch, self.yaw)
    

    def gravity (self):
        g = sum(self.mass_map.m_qdrn) * -self.g
        F = vec(0, 0, g)
        self.translational_motion(F)

        self.to_horizon_vec(F, reverse=True)
        split = self.mass_map.m_qdrn / sum(self.mass_map.m_qdrn)
        splited_F = [s*F for s in split]
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
        F = vec(0, 0, sum(motors))
        F = self.to_horizon_vec(F)
        self.translational_motion(F)
        self.rotational_motion(motors)


    def setTarget (self, target_roll, target_pitch, target_yaw):
        self.target_roll  = target_roll
        self.target_pitch = target_pitch
        self.target_yaw   = target_yaw


    def translational_motion(self, F):
        # a to v
        a = F / self.m
        self.v += a

        # v to s
        self.pos    += self.v
        self.cg_pos += self.v
    

    def to_horizon_vec (self, a: vec, reverse=False):
        r, p, y = self.roll.ang, self.pitch.ang, self.yaw.ang
        if reverse:
           r, p, y = -r, -p, -y

        ROLL = np.array([
            1,      0,       0,
            0, cos(p),  sin(r),
            0, -sin(r), cos(r)

        ])
        PITCH = np.array([
            cos(p), 0, -sin(p),
            0,      1,       0,
            sin(p), 0,  cos(p)

        ])
        YAW = np.array([
            cos(y),  sin(y), 0,
            -sin(y), cos(y), 0,
            0,            0, 1

        ])
        a = np.array([a.x, a.y, a.z]).reshape([3, 1])

        return ROLL@PITCH@YAW@a


    def rotational_motion(self, F: list):
        # alpha -> w
        self.roll.w   += ( (F[2] + F[3]) - (F[1] + F[4]) ) / self.mass_map.I
        self.pitch.w  += ( (F[3] + F[4]) - (F[1] + F[2]) ) / self.mass_map.I

        # w -> theta
        self.roll.ang  += self.roll.w
        self.pitch.ang += self.pitch.w

        # An object forced in space rotates around the center of gravity.
        # But I can rotate the object only on center of object.
        # So the displacement of the center point shall be corrected.
        r, p = self.roll.ang, self.pitch.ang
        cg_to_c = abs(self.pos.x - self.cg_pos.x)
        self.pos += vec(-cg_to_c * cos(r), cg_to_c * sin(r), 0)

        cg_to_c = abs(self.pos.z - self.cg_pos.z)
        self.pos += vec(0, cg_to_c * sin(p), cg_to_c * cos(p))



    class Axis:
        def __init__(self, K_out=None, K_in=None) -> None:
            self.ang = 0
            self.w = 0

            self.ang_control = self.PID()
            self.w_control   = self.PID()

            self.K_out = self.K(K_out)
            self.K_in  = self.K(K_in)

        def pid_control (self, target_ang):
            e = target_ang - self.ang
            return self.ang_control.pid(e, self.K_out)
        
        def double_pid_control (self, target_ang):
            target_w =  self.pid_control(target_ang)

            e = target_w - self.w
            return self.w_control.pid(e, self.K_in)



    class PID:
        def __init__(self) -> None:
            self.e_sum = 0              # for i control
            self.before_e = None        # for d control

        def pid (self, e, K):
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
            if K is not None:
                self.setK(K)

        def setK (self, K: list):
            self.p = K[0]
            self.i = K[1]
            self.d = K[2]





if __name__ == "__main__":
    drone = Drone('model/mavic.obj', 'mass/test.csv')