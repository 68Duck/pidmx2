from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys
from save_window import Save_window


class Save_stage_window(Save_window):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Save Stage Window")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Save_stage_window()
    win.show()
    sys.exit(app.exec_())
