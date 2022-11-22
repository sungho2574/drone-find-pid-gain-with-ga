from vpython import *
from pywavefront import Wavefront



class Model:
    def __init__(self, obj_path) -> None:
        self.model = self.obj_to_triangles(Wavefront(obj_path))
        self.model.visible = True
        self.model.pos = vec(0, 0, 0)

        self.roll  = 0
        self.pitch = 0
        self.yaw   = 0

        # reference axises
        self.roll_axis  = cylinder(pos=vec(0, 0, 0), axis=vec(0, 0, 10), radius=0.01, color=vec(255, 255, 255))
        self.pitch_axis = cylinder(pos=vec(0, 0, 0), axis=vec(10, 0, 0), radius=0.01, color=vec(255, 255, 255))
        self.yaw_axis   = cylinder(pos=vec(0, 0, 0), axis=vec(0, 10, 0), radius=0.01, color=vec(255, 255, 255))

        # sub axises, which spin with model
        self.roll_guide  = cylinder(pos=vec(0, 0, 0), axis=vec(0, 0, 10), radius=0.01, color=vec(255, 0, 0))
        self.pitch_guide = cylinder(pos=vec(0, 0, 0), axis=vec(10, 0, 0), radius=0.01, color=vec(0, 0, 255))
        self.yaw_guide   = cylinder(pos=vec(0, 0, 0), axis=vec(0, 10, 0), radius=0.01, color=vec(0, 255, 0))

        # # reference axises
        # self.roll_axis  = cylinder(pos=vec(0, 0, -5), axis=vec(0, 0, 10), radius=0.01, color=vec(255, 255, 255))
        # self.pitch_axis = cylinder(pos=vec(-5, 0, 0), axis=vec(10, 0, 0), radius=0.01, color=vec(255, 255, 255))
        # self.yaw_axis   = cylinder(pos=vec(0, -5, 0), axis=vec(0, 10, 0), radius=0.01, color=vec(255, 255, 255))

        # # sub axises, which spin with model
        # self.roll_guide  = cylinder(pos=vec(0, 0, -5), axis=vec(0, 0, 10), radius=0.01, color=vec(255, 0, 0))
        # self.pitch_guide = cylinder(pos=vec(-5, 0, 0), axis=vec(10, 0, 0), radius=0.01, color=vec(0, 0, 255))
        # self.yaw_guide   = cylinder(pos=vec(0, -5, 0), axis=vec(0, 10, 0), radius=0.01, color=vec(0, 255, 0))
    

    def pos (self, pos):                        # input is not delta
        self.model.pos = pos

        # reference axises
        # self.roll_axis.pos  = pos + vec(0, 0, -5)
        # self.pitch_axis.pos = pos + vec(-5, 0, 0)
        # self.yaw_axis.pos   = pos + vec(0, -5, 0)

        # sub axises, which spin with model
        self.roll_guide.pos  = pos
        self.pitch_guide.pos = pos
        self.yaw_guide.pos   = pos


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

        self.rotate(self.model,       self.delta_roll, self.delta_pitch, self.delta_yaw)
        self.rotate(self.roll_guide,  self.delta_roll, self.delta_pitch, self.delta_yaw)
        self.rotate(self.pitch_guide, self.delta_roll, self.delta_pitch, self.delta_yaw)
        self.rotate(self.yaw_guide,   self.delta_roll, self.delta_pitch, self.delta_yaw)
    

    def rotate (self, obj, delta_roll, delta_pitch, delta_yaw):
        obj.rotate(angle=(delta_roll),  axis=vector(0, 0, 1), origin=self.model.pos)
        obj.rotate(angle=(delta_pitch), axis=vector(1, 0, 0), origin=self.model.pos)
        obj.rotate(angle=(delta_yaw),   axis=vector(0, 1, 0), origin=self.model.pos)


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
    scene.height = 1000
    scene.width = 1000

    mavic = Model('model/mavic.obj')

    i = 0 
    while True:
        rate(60)
        mavic.ang(radians(i), -radians(i), radians(i))
        i += 1

