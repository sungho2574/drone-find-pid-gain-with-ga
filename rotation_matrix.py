from vpython import *

import numpy as np


roll, pitch, yaw = radians(-45), radians(0), radians(0)

def rotation_matrix (F: vec, reverse=False):
    # input:  the groud coordinate system
    # output: the body coordinate system
    # 지면좌표계로 측정한 힘이, 기울어진 동체좌표계 기준으로 어떻게 측정되는지 변환

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

    # vpython coordinate system and rotation matrix coordinate system is different
    # rotation_matrix(x, y, z) = vpython(z, x, y)
    F = np.array([F.z, F.x, F.y]).reshape([3, 1])

    rotated_F = ROLL@PITCH@YAW@F
    rotated_F = vec(rotated_F[0][0], rotated_F[1][0], rotated_F[2][0])
    return vec(rotated_F.y, rotated_F.z, rotated_F.x)




F = vec(0, 2**(1/2), 0)
# F = vec(0, 0, 2**(1/2))
#F = vec(2**(1/2), 0, 0)
print(rotation_matrix(F))