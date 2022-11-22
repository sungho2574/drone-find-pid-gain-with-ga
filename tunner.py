from vpython import *
from drone import Drone


class Tunner:
    def __init__(self) -> None:
        self.gui()
        self.drone = Drone()
        self.drone.use_double_pid = False

        self.Kout = self.drone.PID.K([10, 0, 0])
        self.K    = self.drone.PID.K()
    

    def simulate (self):
        t = 0
        while True:
            t += 1
            #self.drone.time_step()
            self.graph.plot(t, self.drone.roll.ang, self.drone.pitch.ang, self.drone.yaw.ang)
            print('-----------------------------------------------')


            self.drone.pos = vec(0, 0, 0)
            self.drone.v = vec(0, 0, 0)
            self.drone.pitch.ang = 0
            self.drone.pitch.w = 0


    def gui (self) -> None:
        scene.align = 'left'
        scene.width, scene.height = 1050, 800
        self.graph = self.Graph()

        self.msg("<b> test codition</b>\n")
        winput(bind=self.setStartAngle,  type='numeric', text=0)
        self.msg("  to  ")
        winput(bind=self.setTargetAngle, type='numeric', text=0)
        self.msg("   degree")
        self.msg("\n\n")

        self.msg("<b> angle control<b>")
        self.msg("\n P gain: \t\t");    winput(bind=self.setKoutp, type='numeric', text=0)
        self.msg("\n\n")

        self.msg("<b> w control<b>")
        self.msg("\n P gain: \t\t");    winput(bind=self.setKp, type='numeric', text=0)
        self.msg("\n\n I gain: \t\t");  winput(bind=self.setKi, type='numeric', text=0)
        self.msg("\n\n D gain: \t\t");  winput(bind=self.setKd, type='numeric', text=0)
        self.msg('\n\n')

        self.radio_pid        = radio(text='pid',        checked=True,  name='pid',        bind=self.choose_pid)
        self.msg('\t\t\t\t')
        self.radio_double_pid = radio(text='double pid', checked=False, name='double_pid', bind=self.choose_pid)
        self.msg("\t\t\t\t")
        button(bind=self.Start, text='start')
        self.msg('\n\n')
    
    def msg (self, text):
        wtext(text=text)

    def setStartAngle (self, s):
        self.start_ang = s.number
    
    def setTargetAngle (self, s):
        self.target_ang = s.number

    def setKoutp (self, s):
        self.Kout.p = s.number

    def setKp (self, s):
        self.K.p = s.number

    def setKi (self, s):
        self.K.i = s.number

    def setKd (self, s):
        self.K.d= s.number

    def choose_pid (self, r):
        if r.name == 'pid':
            self.radio_pid.checked        = True
            self.radio_double_pid.checked = False
            self.drone.use_double_pid = False
        else:
            self.radio_pid.checked        = False
            self.radio_double_pid.checked = True
            self.drone.use_double_pid = True
    
    def Start (self, b):
        self.drone.__init__()
        self.graph.clear()

        self.roll.ang = self.start_ang
        self.drone.setTarget(self.target_ang, self.target_ang, self.target_ang)
        self.drone.roll.ang_control.K.setK([self.Kout.p, 0, 0])
        self.drone.roll.w_control.K.setK([self.K.p, self.K.i, self.K.d])
        


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
        
        def plot (self, t, roll, pitch, yaw):
            self.roll.plot(t, roll)
            self.pitch.plot(t, pitch)
            self.yaw.plot(t, yaw)
        
        def clear (self):
            self.roll.delete()
            self.pitch.delete()
            self.yaw.delete()




if __name__ == "__main__":
    tunner = Tunner()
    tunner.simulate()
