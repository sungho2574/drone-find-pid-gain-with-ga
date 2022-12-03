from vpython import *
from drone import Drone

import os
import pickle



class Lab:
    def __init__(self, graph_limit=True) -> None:
        self.drone = Drone(graph_limit=graph_limit)
        self.drone.setLockPos(True)
        self.TEST_DELAY = False
        self.fetch_setting()

    def start_test(self):
        while True:
            sleep(0.1)
            self.drone.time_step()

            if self.interrupt_occurred():
                self.fetch_setting()

                if self.TEST_DELAY:
                    self.drone.time_step()
                    sleep(1)

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
                self.drone.init_pid()

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
            raise Exception("'./lab/lab_setting.pickle' doesn't exist. "
                           +"Please open 'tunner.py' first to initialize lab setting")
        
    def setTestDelay (self, b):
        self.TEST_DELAY = b




if __name__ == '__main__':
    lab = Lab(graph_limit=False)
    lab.setTestDelay(True)
    lab.start_test()