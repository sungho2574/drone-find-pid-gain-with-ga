from vpython import *



class GUI:
    def __init__(self) -> None:
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
        self.Kout_p = s.number

    def setKp (self, s):
        self.Kp = s.number

    def setKi (self, s):
        self.Ki = s.number

    def setKd (self, s):
        self.Kd= s.number

    def choose_pid (self, r):
        if r.name == 'pid':
            self.radio_double_pid.checked = False
            self.drone.use_double_pid = False
        else:
            self.radio_pid.checked = False
            self.drone.use_double_pid = True
    
    def Start (self, b):
        self.drone.__init__()
        self.time = 0
        self.graph.clear()

        self.drone.setTarget(r, p, y)
        self.drone.roll.ang_control.K.setK([self.Kout_p, 0, 0])
        self.drone.roll.w_control.K.setK([self.Kp, self.Ki, self.Kd])
    


    class Graph:
        def __init__(self) -> None:
            self.f1 = graph(align='right', width=600, height=180, title='roll', ymin=-180, ymax=180)
            self.roll = gcurve(graph=self.f1, color=color.red)
            self.roll.plot(0, 0)

            self.f2 = graph(align='right', width=600, height=180, title='pitch', ymin=-90, ymax=90)
            self.pitch = gcurve(graph=self.f2, color=color.red)
            self.pitch.plot(0, 0)


            self.f3 = graph(align='right', width=600, height=180, title='yaw', ymin=-180, ymax=180)
            self.yaw = gcurve(graph=self.f3, color=color.red)
            self.yaw.plot(0, 0)
        
        def plot (self):
            self.roll.plot( self.time, self.drone.roll.ang)
            self.pitch.plot(self.time, self.drone.pitch.ang)
            self.yaw.plot(  self.time, self.drone.yaw.ang)
        
        def clear (self):
            self.roll.delete()
            self.pitch.delete()
            self.yaw.delete()