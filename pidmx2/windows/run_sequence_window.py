from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

class Run_sequence_window(QMainWindow,uic.loadUiType(os.path.join("ui","run_sequence_window.ui"))[0]):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Run Sequence Window")
        self.initUI()

    def initUI(self):
        pass




if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Run_sequence_window()
    win.show()
    sys.exit(app.exec_())
