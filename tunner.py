import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic

from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem

import os
import pickle
import numpy as np

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("tunner_gui.ui")[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.path = './lab/lab_setting.pickle'
        self.read_lab_setting()
        self.plot_lab_setting()

        self.apply_btn.clicked.connect(self.apply)
        self.radio_pid.clicked.connect(self.setPID)
        self.radio_double_pid.clicked.connect(self.setPID)
        self.lock_roll.clicked.connect(self.setLockRoll)
        self.lock_pitch.clicked.connect(self.setLockPitch)
        self.lock_yaw.clicked.connect(self.setLockYaw)


    def read_lab_setting (self):
        if os.path.isfile(self.path):
            with open(self.path, 'rb') as f:
                self.setting = pickle.load(f)
        else:
            self.init_lab_setting()
    

    def init_lab_setting (self):
        self.setting = dict()
        self.setting['condition'] = np.zeros((2, 3))
        self.setting['gain']      = np.zeros((6, 3))
        self.setting['double_pid'] = False
        self.setting['lock_roll']  = False
        self.setting['lock_pitch'] = True
        self.setting['lock_yaw']   = True

        with open(self.path, 'wb') as f:
            pickle.dump(self.setting, f)


    def plot_lab_setting (self):
        # condition_table
        for i in range(2):
            for j in range(3):
                item = QTableWidgetItem(str(self.setting['condition'][i, j]))
                self.condition_table.setItem(i, j, item)
        
        # gain_table
        for i in range(6):
            for j in range(3):
                item = QTableWidgetItem(str(self.setting['gain'][i, j]))
                self.gain_table.setItem(i, j, item)
        
        # pid or double_pid
        self.radio_pid.setChecked(not self.setting['double_pid'])
        self.radio_double_pid.setChecked(self.setting['double_pid'])
        
        # roll, pitch, yaw lock
        self.lock_roll.setChecked(self.setting['lock_roll'])
        self.lock_pitch.setChecked(self.setting['lock_pitch'])
        self.lock_yaw.setChecked(self.setting['lock_yaw'])
    
    
    def setPID (self):
        self.setting['double_pid'] = self.radio_double_pid.isChecked()
    
    def setLockRoll (self):
        self.setting['lock_roll']  = self.lock_roll.isChecked()

    def setLockPitch (self):
        self.setting['lock_pitch'] = self.lock_pitch.isChecked()
    
    def setLockYaw (self):
        self.setting['lock_yaw']   = self.lock_yaw.isChecked()
    
    def apply (self):
        self.save_lab_setting()
        self.occuer_intterupt()
    
    def save_lab_setting (self):
        self.read_condition_table()
        self.read_gain_table()
        
        with open(self.path, 'wb') as f:
            pickle.dump(self.setting, f)
    
    def read_condition_table (self):
        for i in range(2):
            for j in range(3):
                self.setting['condition'][i, j] = float(self.condition_table.item(i, j).text())
    
    def read_gain_table (self):
        for i in range(6):
            for j in range(3):
                self.setting['gain'][i, j] = float(self.gain_table.item(i, j).text())
    
    def occuer_intterupt (self):
        with open('./lab/interrupt.txt', 'w') as f:
            # just make a file
            pass
    
    

if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass() 

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()