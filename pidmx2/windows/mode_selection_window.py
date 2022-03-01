from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.error_window import Error_window

class Mode_selection_window(QWidget,uic.loadUiType(os.path.join("windows/ui","mode_selection_window.ui"))[0]):
    def __init__(self,light_display):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Mode Selection Window")
        self.light_display = light_display
        self.initUI()

    def initUI(self):
        self.submit_button.clicked.connect(self.submit_pressed)
        self.back_button.clicked.connect(self.back_pressed)

    def submit_pressed(self):
        if self.wired_radio.isChecked():
            self.light_display.run_port_selection_window()
            self.close()
        elif self.raspberry_pi_radio.isChecked():
            self.light_display.run_ip_address_selection_window()
            self.close()
        elif self.without_dmx_radio.isChecked():
            self.light_display.no_DMX()
            self.close()
        else:
            raise Exception("No radio was selected.") #The program should never reach here


    def keyPressEvent(self,e): #on the enter key being pressed, call the submit_pressed function
        if e.key() == Qt.Key_Return:
            self.submit_pressed()

    def back_pressed(self):
        self.light_display.run_logon_window()
        self.close()
