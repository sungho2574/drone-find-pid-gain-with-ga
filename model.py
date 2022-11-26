from vpython import *
from pywavefront import Wavefront



class Model:
    def __init__(self, obj_path, visible=True) -> None:
        if not visible:
            pass
            # obj_to_triangles에서 처리 시간 많이 필요함
            # 어차피 visible=False 처리하고 좌표만 다룰 거면 불러올 이유가 없음

        # MAVIC 3D 모델 + 보조축 으로 모델 생성
        mavic = self.obj_to_triangles(Wavefront(obj_path))
        roll_axis  = cylinder(pos=vec(0, 0, -5), axis=vec(0, 0, 10), radius=0.01, color=vec(255, 0, 0))
        pitch_axis = cylinder(pos=vec(-5, 0, 0), axis=vec(10, 0, 0), radius=0.01, color=vec(0, 0, 255))
        yaw_axis   = cylinder(pos=vec(0, -5, 0), axis=vec(0, 10, 0), radius=0.01, color=vec(0, 255, 0))
        
        mavic.pos = vec(0, 0, 0)
        self.model = compound([roll_axis, pitch_axis, yaw_axis, mavic])

        # reference axises
        self.z_axis = cylinder(pos=vec(0, 0, -5), axis=vec(0, 0, 10), radius=0.01, color=vec(255, 255, 255))
        self.x_axis = cylinder(pos=vec(-5, 0, 0), axis=vec(10, 0, 0), radius=0.01, color=vec(255, 255, 255))
        self.y_axis = cylinder(pos=vec(0, -5, 0), axis=vec(0, 10, 0), radius=0.01, color=vec(255, 255, 255))


    def pos (self, pos: vec):                   # input is not delta
        self.model.pos = pos
        

    def ang (self, roll, pitch, yaw):           # input is not delta
        # https://toptechboy.com/9-axis-imu-lesson-20-vpython-visualization-of-roll-pitch-and-yaw/
        k = vec(cos(yaw)*cos(roll), sin(roll), sin(yaw)*cos(roll))
        y = vec(0, 1, 0)
        s = cross(k, y)
        v = cross(s, k)
        vrot = v*cos(pitch) + cross(k, v)*sin(pitch)
    
        self.model.axis = k
        self.model.up = vrot


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

    def roll_test ():           # 90 넘기면 안 됨
        for i in range(360):
            rate(60)
            mavic.ang(radians(i), 0, 0)
    
    def pitch_test ():
        # 정상 범위 확인
        for i in range(360):
            rate(60)
            mavic.ang(0, radians(i), 0)
        
    def yaw_test ():
        # 정상 범위 확인
        for i in range(360):
            rate(60)
            mavic.ang(0, 0, radians(i))
    
    def dynamic_test ():
        i = 0
        while True:
            rate(60)
            ang = radians(i)
            mavic.ang(0, ang, ang)
            mavic.pos(vec(3*cos(ang), 0, 3*sin(ang)))
            i +=1

    roll_test()
    pitch_test()
    yaw_test()
    dynamic_test()
