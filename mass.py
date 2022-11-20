# MassMap was referenced to DJI MACIV 4.
# The size of the model was not referenced to MAVIC
# to simplify the dm generation range on the coordinate plane.

# MAVIC 4 profile
# Diagonal Length (except propeller) : 335 mm
# Weight : 743 g

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from vpython import *

# random functions
# np.random.rand(n: shpae)           : [0, 1) 사이의 실수
# np.random.uniform(low, high, size) : 입력된 범위 사이의 균등분포 실수
# np.random.normal(mu, sigma, size)  : 입력된 평균과 분산에 따른 정규분포 실수



class MassMap:
    MAVIC_WEIGHT = 740

    def __init__(self, path=None) -> None:
        if path is not None:
            self.load_mass(path)


    def make_mass (self, name, dm_len=200):
        px = np.random.uniform(low=-12, high=12, size=dm_len)
        py = []
        for i, x in enumerate(px):
            if (i < len(px)/2):         # right-upward range
                if (-12 <= x < -8):     
                    py.append(np.random.uniform(-x-20, x+4))
                elif (-8 <= x  < 8):
                    py.append(np.random.uniform(x-4, x+4))
                elif (8 <= x  <= 12):
                    py.append(np.random.uniform(x-4, -x+20))
            
            else:                       # right-downward range
                if (-12 <= x < -8):
                    py.append(np.random.uniform(-x-4, x+20))
                elif (-8 <= x  < 8):
                    py.append(np.random.uniform(-x-4, -x+4))
                elif (8 <= x  <= 12):
                    py.append(np.random.uniform(x-20, -x+4))
        
        avg_dm = MassMap.MAVIC_WEIGHT/dm_len
        mass = np.random.normal(loc=avg_dm, scale=avg_dm*0.1, size=dm_len)

        # unit conversion (cm -> m, g -> kg)
        px = np.array(px) * 0.01
        py = np.array(py) * 0.01
        mass *= 0.001

        # save as .csv
        mass_map = [[x, y, dm] for x, y, dm in zip(px, py, mass)]
        mass_map = pd.DataFrame(mass_map, columns=['x', 'y', 'dm'])
        mass_map.to_csv(name, index=False)

        self.set_info(mass_map)


    def render_maas (self, path, guide=False, cg_guide=False):
        self.load_mass(path)

        # rescale for plot
        x = self.mass_map.x * 100
        y = self.mass_map.y * 100
        dm = self.mass_map.dm * 1000 * 30
        colors = np.random.rand(len(self.mass_map))

        plt.figure(figsize=(7, 7))
        plt.scatter(x, y, s=dm, c=colors, alpha=0.5, cmap='Spectral', edgecolor='None')
        plt.xlim([-20, 20])
        plt.ylim([-20, 20])
        plt.title( 'Mass: %.2fg' % (self.M * 1000))

        if guide:
            plt.axhline(0, -20, 20, color='gray', linestyle='--', linewidth=1)
            plt.axvline(0, -20, 20, color='gray', linestyle='--', linewidth=1)
            plt.text(10  - 3,  10, round(self.m_qdrn[1] * 1000, 2), fontsize=12)
            plt.text(-10 - 3,  10, round(self.m_qdrn[2] * 1000, 2), fontsize=12)
            plt.text(-10 - 3, -10, round(self.m_qdrn[3] * 1000, 2), fontsize=12)
            plt.text(10  - 3, -10, round(self.m_qdrn[4] * 1000, 2), fontsize=12)
        if cg_guide:
            plt.axhline(-self.cg_pos.x * 100, -20, 20, color='lightgray', linestyle='--', linewidth=1)
            plt.axvline( self.cg_pos.z * 100, -20, 20, color='lightgray', linestyle='--', linewidth=1)

        plt.show()


    def load_mass (self, path):
        mass_map = pd.read_csv(path)
        self.set_info(mass_map)

    
    def set_info (self, mass_map):
        self.mass_map = mass_map
        self.set_inertia()
        self.set_cg()
    

    def set_inertia (self):
        self.I_qdrn = np.zeros(5)
        self.m_qdrn = np.zeros(5)

        for line in self.mass_map.values.tolist():
            x, y, dm = line
            if x >= 0 and y >= 0:                           # quadrant 1
                self.m_qdrn[1] += dm
                self.I_qdrn[1] += self.set_I(x, y, dm)
            elif x < 0 and y > 0:                           # quadrant 2
                self.m_qdrn[2] += dm
                self.I_qdrn[2] += self.set_I(x, y, dm)
            elif x < 0 and y < 0:                           # quadrant 3
                self.m_qdrn[3] += dm
                self.I_qdrn[3] += self.set_I(x, y, dm)
            elif x > 0 and y < 0:                           # quadrant 4
                self.m_qdrn[4] += dm
                self.I_qdrn[4] += self.set_I(x, y, dm)
            
        
        self.I = sum(self.I_qdrn)
        self.M = sum(self.m_qdrn)

    
    def set_I (self, x, y, dm):
        return dm * (x**2 + y**2)
    
            
    def set_cg (self):
        roll_cg = 0
        pitch_cg = 0
        for line in self.mass_map.values.tolist():
            x, y, dm = line
            roll_cg  += x*dm
            pitch_cg += y*dm
        
        roll_cg  /= self.M
        pitch_cg /= self.M

        # apply graphic coordinate
        self.cg_pos = vec(-roll_cg, 0, pitch_cg)

        
    





if __name__ == "__main__":
    map_maker = MassMap()

    path = 'mass/new2.csv'
    map_maker.make_mass(path)
    map_maker.render_maas(path=path, guide=True, cg_guide=True)

       
