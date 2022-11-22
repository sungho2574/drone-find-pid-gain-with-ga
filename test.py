import pandas as pd
import numpy as np
from vpython import *

#scene.resizable = False
scene.align = 'left'
#box()
scene.width, scene.height = 1050, 800







box()

def f (s):
    pass



def T(s): 
    print(s.text, s.number)
def put_text (text):
    wtext(text=text)

put_text("<b> test codition</b>\n")
winput( bind=T , type='numeric', text=1)

put_text("  to ")

winput( bind=T )

put_text("   degree")

put_text("\n\n")
put_text("<b> angle control<b>")
put_text("\n P gain: \t\t")
winput( bind=T )

put_text("\n\n")
put_text("<b> w control<b>")
put_text("\n P gain: \t\t")
winput( bind=T )


put_text("\n\n I gain: \t\t")
winput( bind=T )
put_text("\n\n D gain: \t\t")
winput( bind=T )


def set_aim(r):
    pass

put_text('\n\n')
radio(text='pid', checked=False, bind=set_aim)

put_text('\t\t\t\t\t')
radio(text='double pid', checked=False, bind=set_aim)



put_text("\t\t\t\t")





def B(b):
    print("The button said this: ", b.text)
button( bind=B, text='start' )

put_text('\n\n')


f1 = graph(align='right', width=600, height=180, title='roll', ymin=-180, ymax=180)
g1 = gcurve(graph=f1, color=color.red)
g1.plot(1, 1)

f2 = graph(align='right', width=600, height=180, title='pitch', ymin=-90, ymax=90)
g2 = gcurve(graph=f2, color=color.red)
g2.plot(1, 1)


f3 = graph(align='right', width=600, height=180, title='yaw', ymin=-180, ymax=180)
g3 = gcurve(graph=f3, color=color.red)
g3.plot(1, 1)

