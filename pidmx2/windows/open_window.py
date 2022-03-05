from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

class Open_window(QWidget,uic.loadUiType(os.path.join("windows/ui","open_window.ui"))[0]):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Open Window")
        self.initUI()

    def initUI(self):
        pass
