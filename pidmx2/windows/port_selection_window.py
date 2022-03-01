from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.message_window import Message_window
from windows.error_window import Error_window

class Port_selection_window(QMainWindow,uic.loadUiType(os.path.join("windows/ui","port_selection_window.ui"))[0]):
    def __init__(self,light_display):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Port Selection Window")
        self.light_display = light_display
        self.initUI()

    def initUI(self):
        self.back_button.clicked.connect(self.back_pressed)
        self.submit_button.clicked.connect(self.submit_pressed)
        self.test_port_button.clicked.connect(self.test_port)

    def back_pressed(self):
        self.light_display.run_mode_selection_window()
        self.close()

    def keyPressEvent(self,e): #on the enter key being pressed, call the submit_pressed function
        if e.key() == Qt.Key_Return:
            self.submit_pressed()

    def submit_pressed(self):
        port = self.get_port()
        if self.light_display.test_port(port):
            self.light_display.wired_DMX(port)
            self.close()
        else:
            self.error_window = Error_window("The port you have chosen does not work")

    def get_port(self):
        port = self.port_number_input.value()
        if self.windows_radio.isChecked():
            return f"COM{port}"
        elif self.linux_radio.isChecked():
            return f"/dev/ttyUSB{port}"
        else:
            raise Exception("No radios are checked.") #The program should never reach here

    def test_port(self):
        port = self.get_port()
        self.message_window = Message_window(f"The port you have chosen {'works' if self.light_display.test_port(port) else 'does not work'}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Port_selection_window()
    win.show()
    sys.exit(app.exec_())
