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

    def __init__(self) -> None:
        pass


    def render_maas (self, path):
        mass_map = pd.read_csv(path)

        # rescale for plot
        x = mass_map.x * 100
        y = mass_map.y * 100
        dm = mass_map.dm * 1000 * 30
        colors = np.random.rand(len(mass_map))

        plt.figure(figsize=(7, 7))
        plt.scatter(x, y, s=dm, c=colors, alpha=0.5, cmap='Spectral', edgecolor='None')
        plt.xlim([-20, 20])
        plt.ylim([-20, 20])
        plt.show()


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

        mass = np.random.normal(loc=MassMap.MAVIC_WEIGHT/dm_len, scale=1, size=dm_len) 

        # unit conversion (cm -> m, g -> kg)
        px = np.array(px) * 0.01
        py = np.array(py) * 0.01
        mass *= 0.001

        # save as .csv
        mass_map = [[x, y, dm] for x, y, dm in zip(px, py, mass)]
        mass_map = pd.DataFrame(mass_map, columns=['x', 'y', 'dm'])
        mass_map.to_csv(name, index=False)



if __name__ == "__main__":
    map_maker = MassMap()

    path = 'mass/1.csv'
    map_maker.make_mass(path)
    map_maker.render_maas(path)

       
