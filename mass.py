# MassMap was referenced to DJI MACIV 4.
# The size of the model was not referenced to MAVIC
# to simplify the dm generation range on the coordinate plane.

# MAVIC 4 profile
# Diagonal Length (except propeller) : 335 mm
# Weight : 743 g

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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


    def render_maas (self, path, guide=False):
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
            plt.axhline(0, -20, 20, color='lightgray', linestyle='--', linewidth=1)
            plt.axvline(0, -20, 20, color='lightgray', linestyle='--', linewidth=1)
            plt.text(10  - 3,  10, round(self.quadrant[1], 6), fontsize=12)
            plt.text(-10 - 3,  10, round(self.quadrant[2], 6), fontsize=12)
            plt.text(-10 - 3, -10, round(self.quadrant[3], 6), fontsize=12)
            plt.text(10  - 3, -10, round(self.quadrant[4], 6), fontsize=12)

        plt.show()


    def load_mass (self, path):
        mass_map = pd.read_csv(path)
        self.set_info(mass_map)

    
    def set_info (self, mass_map):
        self.mass_map = mass_map
        self.quadrant = np.zeros(5)
        for line in self.mass_map.values.tolist():
            x, y, dm = line
            if x >= 0 and y >= 0:                           # quadrant 1
                self.quadrant[1] += self.set_I(x, y, dm)
            elif x < 0 and y > 0:                           # quadrant 2
                self.quadrant[2] += self.set_I(x, y, dm)
            elif x < 0 and y < 0:                           # quadrant 3
                self.quadrant[3] += self.set_I(x, y, dm)
            elif x > 0 and y < 0:                           # quadrant 4
                self.quadrant[4] += self.set_I(x, y, dm)
        
        self.I = sum(self.quadrant)
        self.M = self.mass_map.dm.values.sum()
    

    def set_I (self, x, y, dm):
        return dm * (x**2 + y**2)
            




if __name__ == "__main__":
    map_maker = MassMap()

    path = 'mass/test.csv'
    #map_maker.make_mass(path)
    map_maker.render_maas(path=path, guide=True)

       
