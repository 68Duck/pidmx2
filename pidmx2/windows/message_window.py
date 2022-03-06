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




if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Message_window("This is placeholder text for the message window. In the actual window the message displayed here will be relevent to the senario in which the message window was opened")
    win.show()
    sys.exit(app.exec_())
