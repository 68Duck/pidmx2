from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

class Error_window(QWidget,uic.loadUiType(os.path.join("windows/ui","error_window.ui"))[0]):
    def __init__(self,message):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Error Window")
        self.message = message
        self.initUI()
        self.show()

    def initUI(self):
        self.error_message.setText(self.message)
        self.ok_button.clicked.connect(self.ok_pressed)

    def ok_pressed(self):
        self.close()

    def keyPressEvent(self,e): #on the enter key being pressed, call the submit_pressed function
        if e.key() == Qt.Key_Return:
            self.ok_pressed()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Error_window("This is placeholder text for the error window. In the actual window the message displayed here will be relevent to the senario in which the error window was opened")
    win.show()
    sys.exit(app.exec_())
