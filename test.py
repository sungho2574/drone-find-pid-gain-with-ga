import pandas as pd
import numpy as np
from vpython import *

roll = radians(45)
pitch = radians(0)
yaw = radians(0)

def rotation_matrix (F: vec, reverse=False):
        # vpython coordinate system and rotation matrix coordinate system is different
        # vpython(x, y, z) = rotation_matrix(z, y, x)
        r, p, y = roll, pitch, yaw
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

F = vec(2**(1/2), 0, 0)
# F = vec(0, 0, 0)
# a = np.array([F.x, F.y, F.z]).reshape([3, 1])
# print(F.x, F.y, F.z)
# print(a)
print(rotation_matrix(F))
