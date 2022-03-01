from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

class Record_playback_window(QMainWindow,uic.loadUiType(os.path.join("ui","record_playback_window.ui"))[0]):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Record Playback Window")
        self.initUI()

    def initUI(self):
        pass




if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Record_playback_window()
    win.show()
    sys.exit(app.exec_())
