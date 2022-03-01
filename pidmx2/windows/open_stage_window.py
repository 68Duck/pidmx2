from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys
from open_window import Open_window


class Open_stage_window(Open_window):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Open Stage Window")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Open_stage_window()
    win.show()
    sys.exit(app.exec_())
