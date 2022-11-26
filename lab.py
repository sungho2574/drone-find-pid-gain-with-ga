from vpython import *
from drone import Drone

import os
import pickle



class Lab:
    def __init__(self) -> None:
        self.drone = Drone()
        self.drone.setLockPos(True)
        self.fetch_setting()

    def start_test(self):
        while True:
            sleep(0.1)
            self.drone.time_step()

            if self.interrupt_occurred():
                self.fetch_setting()

    def interrupt_occurred (self):
        path = './lab/interrupt.txt'
        if os.path.isfile(path):
            os.remove(path)
            return True
        else:
            return False
    
    def fetch_setting (self):
        path = './lab/lab_setting.pickle'
        if os.path.isfile(path):
            with open(path, 'rb') as f:
                setting = pickle.load(f)

                self.drone.clear_graph()
                self.drone.reset_physical_quantity()

                start_ang  = setting['condition'][0]
                target_ang = setting['condition'][1]
                self.drone.setAng(start_ang[0], start_ang[1], start_ang[2])
                self.drone.setTarget(target_ang[0], target_ang[1], target_ang[2])

                self.drone.setK(setting['gain'])
                self.drone.setDoublePID(setting['double_pid'])
                self.drone.setLockRoll(not setting['chk_roll'])
                self.drone.setLockPITCH(not setting['chk_pitch'])
                self.drone.setLockYaw(not setting['chk_yaw'])
        else:
            print("'./lab/lab_setting.pickle' doesn't exist.")
            print("Please open 'tunner.py' first to initialize lab setting")
            exit()



if __name__ == '__main__':
    lab = Lab()
    lab.start_test()