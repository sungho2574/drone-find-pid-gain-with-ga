from drone import Drone

import os


class Lab:
    def __init__(self) -> None:
        self.drone = Drone()

    def start_test(self):
        while True:
            self.drone.time_step()

            if self.event_occured():
                # 설정을 드론에 적용
                pass
    
    def interrupt_occurred (self):
        path = './lab/interrupt.txt'
        if os.path.isfile(path):
            os.remove(path)
            return True
        else:
            return False



if __name__ == '__main__':
    lab = Lab()
    lab.start_test()