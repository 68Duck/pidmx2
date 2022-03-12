from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

class Message_window(QWidget,uic.loadUiType(os.path.join("windows/ui","message_window.ui"))[0]):
    def __init__(self,message):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Message Window")
        self.message = message
        self.initUI()
        self.show()

    def initUI(self):
        self.message_label.setText(self.message)
        self.ok_button.clicked.connect(self.close)

    def keyPressEvent(self,e):
        if e.key() == Qt.Key_Return:
            self.close()
