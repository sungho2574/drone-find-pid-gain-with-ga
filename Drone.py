from vpython import *

from model import Model
from mass import MassMap


class Drone:
    def __init__(self, model_path, dm_path) -> None:
        self.model = Model(model_path)
        self.mass_map = MassMap(dm_path)

        self.m = self.mass_map.total_mass
        self.pos = vec(0, 0, 0)
        self.v = vec(0, 0, 0)

        self.roll  = Axis()
        self.pitch = Axis()
        self.yaw   = Axis()


class Axis:
    def __init__(self) -> None:
        pass

if __name__ == "__main__":
    drone = Drone('model/mavic.obj', 'mass/test.csv')