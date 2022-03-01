from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

class Confirm_window(QWidget,uic.loadUiType(os.path.join("ui","confirm_window.ui"))[0]):
    def __init__(self,message):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Confirm Window")
        self.message = message
        self.initUI()

    def initUI(self):
        self.confirm_message.setText(self.message)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Confirm_window("This is placeholder text for the confirm window. In the actual window the message displayed here will be relevent to the senario in which the confirm window was opened")
    win.show()
    sys.exit(app.exec_())
