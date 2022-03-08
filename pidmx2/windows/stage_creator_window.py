from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

class Stage_creator_window(QMainWindow,uic.loadUiType(os.path.join("windows/ui","stage_creator_window.ui"))[0]):
    def __init__(self,light_display,database_manager):
        super().__init__()
        self.setupUi(self)
        self.light_display = light_display
        self.database_manager = database_manager
        self.setWindowTitle("Stage Creator Window")
        self.initUI()

    def initUI(self):
        self.square_label_1.hide()
        self.square_label_2.hide()
