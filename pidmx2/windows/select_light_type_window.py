from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.error_window import Error_window

class Select_light_type_window(QWidget,uic.loadUiType(os.path.join("windows/ui","select_light_type_window.ui"))[0]):
    def __init__(self,light_display):
        super().__init__()
        self.setupUi(self)
        self.light_display = light_display
        self.setWindowTitle("Select Light Type Window")
        self.initUI()

    def initUI(self):
        self.select_button.clicked.connect(self.select_pressed)
        self.cancel_button.clicked.connect(self.close)
        drop_down_items = []
        for fixture in self.light_display.get_fixtures():
            if fixture is not None:
                drop_down_items.append(fixture.get_light_type())

        drop_down_items = set(drop_down_items)
        for item in drop_down_items:
            self.drop_down.addItem(item)

    def select_pressed(self):
        light_type = self.drop_down.currentText()
        if light_type == "":
            self.error_window = Error_window("There are no patched lights. Please try patching one before selecting one")
            return
        self.light_display.select_light_type(light_type)
        self.close()

    def keyPressEvent(self,e):
        if e.key() == Qt.Key_Return:
            self.select_pressed()
