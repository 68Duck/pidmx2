from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys
import time

from windows.error_window import Error_window
from windows.message_window import Message_window

class Raspberry_pi_password_input_window(QWidget,uic.loadUiType(os.path.join("windows/ui","raspberry_pi_password_input_window.ui"))[0]):
    def __init__(self,light_display):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Raspberry Pi Logon Window")
        self.light_display = light_display
        self.initUI()
        self.show()

    def initUI(self):
        self.submit_button.clicked.connect(self.submit_pressed)
        self.back_button.clicked.connect(self.back_pressed)
        self.password_input.setFocus()

    def submit_pressed(self):
        self.password = self.password_input.text()
        self.message_window = Message_window("Connecting...")
        QTimer.singleShot(0,self.attempt_login)

    def attempt_login(self):
        result = self.light_display.raspberry_pi_login(self.password)
        self.message_window.close()
        if result is True:
            self.close()
        else:
            self.error_window = Error_window(str(result))
            self.password_input.setText("")

    def keyPressEvent(self,e): #on the enter key being pressed, call the submit_pressed function
        if e.key() == Qt.Key_Return:
            self.submit_pressed()


    def back_pressed(self):
        self.light_display.run_ip_address_selection_window()
        self.close()

class Thread(QThread):
    def __init__(self,parent=None):
        QThread.__init__(self,parent)
    def run(self):
        self.message_window = Message_window("Connecting...")
        self.message_window.show()
    def close(self):
        try:
            self.message_window.close()
        except:
            raise Exception("Message window was not defined")
