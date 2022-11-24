from vpython import *
from pywavefront import Wavefront

import numpy as np

class Model:
    def __init__(self, obj_path, visible=True) -> None:
        if not visible:
            pass
            # obj_to_triangles에서 처리 시간 많이 필요함
            # 어차피 visible=False 처리하고 좌표만 다룰 거면 불러올 이유가 없음

        self.model = self.obj_to_triangles(Wavefront(obj_path))
        self.model.pos = vec(0, 0, 0)

        self.roll  = 0
        self.pitch = 0
        self.yaw   = 0

        # roll, pitch, yaw axises
        self.roll_axis  = vec(0, 0, 1)
        self.pitch_axis = vec(1, 0, 0)
        self.yaw_axis   = vec(0, 1, 0)

        # reference axises
        self.z_axis = cylinder(pos=vec(0, 0, -5), axis=vec(0, 0, 10), radius=0.01, color=vec(255, 255, 255))
        self.x_axis = cylinder(pos=vec(-5, 0, 0), axis=vec(10, 0, 0), radius=0.01, color=vec(255, 255, 255))
        self.y_axis = cylinder(pos=vec(0, -5, 0), axis=vec(0, 10, 0), radius=0.01, color=vec(255, 255, 255))

        # sub axises, which spin with model
        self.roll_b  = cylinder(pos=vec(0, 0, 0), axis=vec(0, 0, -5), radius=0.01, color=vec(255, 0, 0))
        self.roll_f  = cylinder(pos=vec(0, 0, 0), axis=vec(0, 0,  5), radius=0.01, color=vec(255, 0, 0))
        self.pitch_r = cylinder(pos=vec(0, 0, 0), axis=vec(-5, 0, 0), radius=0.01, color=vec(0, 0, 255))
        self.pitch_l = cylinder(pos=vec(0, 0, 0), axis=vec( 5, 0, 0), radius=0.01, color=vec(0, 0, 255))
        self.yaw_b   = cylinder(pos=vec(0, 0, 0), axis=vec(0, -5, 0), radius=0.01, color=vec(0, 255, 0))
        self.yaw_t   = cylinder(pos=vec(0, 0, 0), axis=vec(0,  5, 0), radius=0.01, color=vec(0, 255, 0))
    

    def pos (self, pos):                        # input is not delta
        self.model.pos = pos
        self.roll_b.pos  = pos
        self.roll_f.pos  = pos
        self.pitch_r.pos = pos
        self.pitch_l.pos = pos
        self.yaw_b.pos   = pos
        self.yaw_t.pos   = pos


    def ang (self, roll, pitch, yaw):           # input is not delta
        # there is only rotate method
        # but i want to get input as roll, pitch, yaw, which is not delta angle
        # so i sperate angle method and rotate method
        self.delta_roll  = roll -  self.roll
        self.delta_pitch = pitch - self.pitch
        self.delta_yaw   = yaw -   self.yaw

        self.roll  += self.delta_roll
        self.pitch += self.delta_pitch
        self.yaw   += self.delta_yaw

        self.rotate(self.model,   self.delta_roll, self.delta_pitch, self.delta_yaw)
        self.rotate(self.roll_b,  self.delta_roll, self.delta_pitch, self.delta_yaw)
        self.rotate(self.roll_f,  self.delta_roll, self.delta_pitch, self.delta_yaw)
        self.rotate(self.pitch_r, self.delta_roll, self.delta_pitch, self.delta_yaw)
        self.rotate(self.pitch_l, self.delta_roll, self.delta_pitch, self.delta_yaw)
        self.rotate(self.yaw_b,   self.delta_roll, self.delta_pitch, self.delta_yaw)
        self.rotate(self.yaw_t,   self.delta_roll, self.delta_pitch, self.delta_yaw)
        
        self.update_reference_axis(self.delta_roll, self.delta_pitch, self.delta_yaw)
    

    def rotate (self, obj, delta_roll, delta_pitch, delta_yaw):
        roll_axis  = self.roll_axis 
        pitch_axis = self.pitch_axis
        yaw_axis   = self.yaw_axis

        obj.rotate(angle=delta_roll,  axis=roll_axis,  origin=self.model.pos)
        pitch_axis = self.rotation_matrix(pitch_axis, delta_roll, 0, 0)
        yaw_axis   = self.rotation_matrix(yaw_axis,   delta_roll, 0, 0)

        obj.rotate(angle=delta_pitch, axis=pitch_axis, origin=self.model.pos)
        roll_axis  = self.rotation_matrix(roll_axis, 0, delta_pitch, 0)
        yaw_axis   = self.rotation_matrix(yaw_axis,  0, delta_pitch, 0)

        obj.rotate(angle=delta_yaw,   axis=yaw_axis,   origin=self.model.pos)
    

    def update_reference_axis (self, delta_roll, delta_pitch, delta_yaw):
        # roll_axis
        self.pitch_axis = self.rotation_matrix(self.pitch_axis, delta_roll, 0, 0)
        self.yaw_axis   = self.rotation_matrix(self.yaw_axis,   delta_roll, 0, 0)

        # pitch_axis
        self.roll_axis  = self.rotation_matrix(self.roll_axis, 0, delta_pitch, 0)
        self.yaw_axis   = self.rotation_matrix(self.yaw_axis,  0, delta_pitch, 0)

        # yaw_axis
        self.roll_axis  = self.rotation_matrix(self.roll_axis,  0, 0, delta_yaw)
        self.pitch_axis = self.rotation_matrix(self.yaw_axis,   0, 0, delta_yaw)



    def rotation_matrix (self, F: vec, roll, pitch, yaw, reverse=True):
        # input:  the groud coordinate system
        # output: the body coordinate system
        # 지면좌표계로 측정한 힘이, 기울어진 동체좌표계 기준으로 어떻게 측정되는지 변환

        # revers=True인 경우는
        # 현 좌표계 기준으로 벡터를 회전시켰을 때 어떻게 기준축으로 나눠지는가를 계산함

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

    def obj_to_triangles(self, obj):        
        # it makes possible to load obj model in vpython
        # https://groups.google.com/g/vpython-users/c/T3SzNheUOAg

        tris = [] # list of triangles to compound
        ret = [] # will return a list obj compounds if necessary
        # Iterate vertex data collected in each material
        for name, mesh in obj.meshes.items():
            vertices = 0
            curtexture = None
            curcol = vec(1,1,1)
            curopacity = 1.0
            # Contains the vertex format (string) such as "T2F_N3F_V3F"
            # T2F, C3F, N3F and V3F may appear in this string
            for material in mesh.materials:
                # Contains the vertex format (string) such as "T2F_N3F_V3F"
                # T2F, C3F, N3F and V3F may appear in this string
                curopacity = material.transparency
                #print(vars(material))
                #print(vars(material.texture))
                if material.vertex_format == 'V3F':
                    vertex_size = 3
                elif material.vertex_format == 'C3F_V3F':
                    vertex_size = 6
                elif material.vertex_format == 'N3F_V3F':
                    vertex_size = 6
                elif material.vertex_format == 'T2F_V3F':
                    vertex_size = 5
                    curtexture = str(material.texture._path)
                    #curtexture = str(material.texture._search_path) + '/' + material.texture._name
                elif material.vertex_format == 'T2F_C3F_V3F':
                    vertex_size = 8
                    curtexture = str(material.texture._path)
                elif material.vertex_format == 'T2F_N3F_V3F':
                    vertex_size = 8
                    curtexture = str(material.texture._path)
                verts = []
                for i in range(len(material.vertices)//vertex_size):
                    if material.vertex_format == 'V3F':
                        curpos = vec(material.vertices[i*vertex_size],material.vertices[i*vertex_size+1],material.vertices[i*vertex_size+2])
                        verts.append( vertex(pos=curpos) )
                    elif material.vertex_format == 'C3F_V3F':
                        curcol = vec(material.vertices[i*vertex_size],material.vertices[i*vertex_size+1],material.vertices[i*vertex_size+2])
                        curpos = vec(material.vertices[i*vertex_size+3],material.vertices[i*vertex_size+4],material.vertices[i*vertex_size+5])
                        verts.append( vertex(pos=curpos,color=curcol) )
                    elif material.vertex_format == 'N3F_V3F':
                        normal = vec(material.vertices[i*vertex_size],material.vertices[i*vertex_size+1],material.vertices[i*vertex_size+2])
                        curpos = vec(material.vertices[i*vertex_size+3],material.vertices[i*vertex_size+4],material.vertices[i*vertex_size+5])
                        verts.append( vertex(pos=curpos,normal=normal) )
                    elif material.vertex_format == 'T2F_V3F':
                        curtexpos = vec(material.vertices[i*vertex_size],material.vertices[i*vertex_size+1],0)
                        curpos = vec(material.vertices[i*vertex_size+2],material.vertices[i*vertex_size+3],material.vertices[i*vertex_size+4])
                        verts.append( vertex(pos=curpos,texpos=curtexpos) )
                    elif material.vertex_format == 'T2F_C3F_V3F':
                        curtexpos = vec(material.vertices[i*vertex_size],material.vertices[i*vertex_size+1],0)
                        curcol = vec(material.vertices[i*vertex_size],material.vertices[i*vertex_size+1],material.vertices[i*vertex_size+2])
                        curpos = vec(material.vertices[i*vertex_size+5],material.vertices[i*vertex_size+6],material.vertices[i*vertex_size+7])
                        verts.append( vertex(pos=curpos, texpos=curtexpos, color=curcol) )
                    elif material.vertex_format == 'T2F_N3F_V3F':
                        curtexpos = vec(material.vertices[i*vertex_size],material.vertices[i*vertex_size+1],0)
                        normal = vec(material.vertices[i*vertex_size+2],material.vertices[i*vertex_size+3],material.vertices[i*vertex_size+4])
                        curpos = vec(material.vertices[i*vertex_size+5],material.vertices[i*vertex_size+6],material.vertices[i*vertex_size+7])
                        verts.append( vertex(pos=curpos,normal=normal,texpos=curtexpos) )
                        
                    verts[-1].opacity = curopacity
                    if len(verts) == 3:
                        vertices += 3
                        tris.append(triangle(vs=verts))
                        verts=[]

                    if vertices > 64000:
                        print(vertices)
                        if curtexture is not None:
                            ret.append(compound(tris,texture=curtexture))
                        else:
                            ret.append(compound(tris))
                        tris = []
                        vertices = 0
                        
                if curtexture is not None:
                    ret.append(compound(tris,texture=curtexture))
                else:
                    ret.append(compound(tris))
                tris = []
                vertices = 0

        if len(ret) == 1: return ret[0]               
        else: return ret



if __name__ == '__main__':
    scene.width, scene.height = 1000, 800
    mavic = Model('model/mavic.obj')

    i = 0
    while True:
        sleep(0.1)
        # rate(60)
        # mavic.ang(radians(i), -radians(i), radians(i))
        # mavic.pos(vec(3*cos(radians(i)), 0, 3*sin(radians(i))))
        i += 1

        # mavic.ang(radians(i), 0, 0)
        mavic.ang(0, radians(i), 0)

    # mavic.ang(radians(45), radians(-90), 0)
    # # mavic.ang(0, radians(90), 0)
    # print(mavic.roll_axis, mavic.pitch_axis, mavic.yaw_axis)