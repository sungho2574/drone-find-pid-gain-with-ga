# MassMap was referenced to DJI MACIV 4.
# The size of the model was not referenced to MAVIC
# to simplify the dm generation range on the coordinate plane.

# MAVIC 4 profile
# Diagonal Length (except propeller) : 335 mm
# Weight : 743 g

# random functions
# np.random.rand(n: shpae)           : [0, 1) 사이의 실수
# np.random.uniform(low, high, size) : 입력된 범위 사이의 균등분포 실수
# np.random.normal(mu, sigma, size)  : 입력된 평균과 분산에 따른 정규분포 실수

from vpython import *

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



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
        mass_map = pd.DataFrame(mass_map, columns=['x', 'z', 'dm'])
        mass_map.to_csv(name, index=False)

        self.set_info(mass_map)


    def render_maas (self, path, guide=False, axis_guide=False):
        self.load_mass(path)

        # rescale for plot
        x = self.mass_map.x * 100
        z = self.mass_map.z * 100
        dm = self.mass_map.dm * 1000 * 30
        colors = np.random.rand(len(self.mass_map))

        plt.figure(figsize=(7, 7))
        plt.scatter(x, z, s=dm, c=colors, alpha=0.5, cmap='Spectral', edgecolor='None')
        plt.xlim(20, -20)
        plt.ylim(-20, 20)
        plt.xlabel('x')
        plt.ylabel('z', rotation=0)
        plt.title( 'Mass: %.2fg' % (self.M * 1000))

        if guide:
            plt.axhline(self.cg_pos.z * 100, -20, 20, color='gray', linestyle='--', linewidth=1)
            plt.axvline(self.cg_pos.x * 100, -20, 20, color='gray', linestyle='--', linewidth=1)
            plt.text( 10,  10, round(self.m_qdrn[1] * 1000, 2), fontsize=13)
            plt.text(-10,  10, round(self.m_qdrn[2] * 1000, 2), fontsize=13)
            plt.text(-10, -10, round(self.m_qdrn[3] * 1000, 2), fontsize=13)
            plt.text( 10, -10, round(self.m_qdrn[4] * 1000, 2), fontsize=13)
        if axis_guide:
            plt.axhline(0, -20, 20, color='lightgray', linestyle='--', linewidth=1)
            plt.axvline(0, -20, 20, color='lightgray', linestyle='--', linewidth=1)


        plt.show()


    def load_mass (self, path):
        mass_map = pd.read_csv(path)
        self.set_info(mass_map)

    
    def set_info (self, mass_map):
        self.mass_map = mass_map
        self.set_cg()
        self.set_inertia()
    

    def set_cg (self):
        x_cg = 0
        z_cg = 0
        for line in self.mass_map.values.tolist():
            x, y, dm = line
            x_cg += x*dm
            z_cg += y*dm
        
        self.M = self.mass_map.dm.values.sum()
        x_cg /= self.M
        z_cg /= self.M
        self.cg_pos = vec(x_cg, 0, z_cg)


    def set_inertia (self):
        self.I_qdrn = np.zeros(5)
        self.m_qdrn = np.zeros(5)
        x_cg = self.cg_pos.x
        z_cg = self.cg_pos.z

        for line in self.mass_map.values.tolist():
            x, z, dm = line
            if x >= x_cg and z >= z_cg:                           # quadrant 1
                self.m_qdrn[1] += dm
                self.I_qdrn[1] += self.set_I(x, z, dm)
            elif x < x_cg and z > z_cg:                           # quadrant 2
                self.m_qdrn[2] += dm
                self.I_qdrn[2] += self.set_I(x, z, dm)
            elif x < x_cg and z < z_cg:                           # quadrant 3
                self.m_qdrn[3] += dm
                self.I_qdrn[3] += self.set_I(x, z, dm)
            elif x > x_cg and z < z_cg:                           # quadrant 4
                self.m_qdrn[4] += dm
                self.I_qdrn[4] += self.set_I(x, z, dm)
        
        self.I = sum(self.I_qdrn)

    
    def set_I (self, x, y, dm):
        return dm * (x**2 + y**2)




if __name__ == "__main__":
    path = 'mass/test.csv'

    map_maker = MassMap()
    #map_maker.make_mass(path)
    map_maker.render_maas(path=path, guide=True, axis_guide=True)