from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

class Ip_address_selection_window(QWidget,uic.loadUiType(os.path.join("windows/ui","ip_address_selection_window.ui"))[0]):
    def __init__(self,light_display,database_manager):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("IP address selection window")
        self.light_display = light_display
        self.database_manager = database_manager
        self.initUI()

    def initUI(self):
        self.submit_button.clicked.connect(self.submit_pressed)
        self.back_button.clicked.connect(self.back_pressed)
        self.retrieve_previous_address()

    def retrieve_previous_address(self):
        addresses = self.database_manager.query_db("SELECT port_1,port_2,port_3,port_4 FROM Ipv4_address")
        if len(addresses) > 0:
            address = addresses[-1]
        else:
            address = {"port_1":0,"port_2":0,"port_3":0,"port_4":0}
        self.port_input_1.setValue(address["port_1"])
        self.port_input_2.setValue(address["port_2"])
        self.port_input_3.setValue(address["port_3"])
        self.port_input_4.setValue(address["port_4"])

    def store_address(self,port_1,port_2,port_3,port_4):
        self.database_manager.query_db("INSERT INTO Ipv4_address(port_1,port_2,port_3,port_4) VALUES(?,?,?,?)",(port_1,port_2,port_3,port_4))

    def back_pressed(self):
        self.light_display.run_mode_selection_window()
        self.close()

    def submit_pressed(self):
        port_1 = self.port_input_1.value()
        port_2 = self.port_input_2.value()
        port_3 = self.port_input_3.value()
        port_4 = self.port_input_4.value()
        ipv4 = str(port_1) + "." + str(port_2) + "." + str(port_3) + "." + str(port_4)
        self.store_address(port_1,port_2,port_3,port_4)
        self.light_display.raspberry_pi_DMX(ipv4)
        self.close()


    def keyPressEvent(self,e): #on the enter key being pressed, call the submit_pressed function
        if e.key() == Qt.Key_Return:
            self.submit_pressed()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Ip_address_selection_window()
    win.show()
    sys.exit(app.exec_())
