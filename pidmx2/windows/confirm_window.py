from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

class Confirm_window(QWidget,uic.loadUiType(os.path.join("windows/ui","confirm_window.ui"))[0]):
    def __init__(self,message):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Confirm Window")
        self.message = message
        self.initUI()

    def initUI(self):
        self.confirm_message.setText(self.message)
