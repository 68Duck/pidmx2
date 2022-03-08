from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.open_window import Open_window
from windows.error_window import Error_window

class Open_rig_window(Open_window):
    def __init__(self,light_display,database_manager):
        super().__init__()
        self.database_manager = database_manager
        self.light_display = light_display
        self.setWindowTitle("Open Rig Window")
        self.initUI()

    def initUI(self):
        self.open_button.clicked.connect(self.open_pressed)
        self.delete_button.clicked.connect(self.delete_pressed)
        account_id = self.light_display.get_account_id()
        rig_ids = self.database_manager.query_db("SELECT rig_id FROM Rigs_in_account WHERE account_id = ?",(account_id,))
        saved_rigs = []
        for id in rig_ids:
            saved_rigs.append(self.database_manager.query_db("SELECT rig_name FROM rigs WHERE rig_id = ?",(id["rig_id"],))[0])
        for rig in saved_rigs:
            self.drop_down.addItem(rig["rig_name"])

    def open_pressed(self):
        rig_name = self.drop_down.currentText()
        if rig_name is None:
            self.error_window = Error_window("No rig was selected. Please try again")
        else:
            rig_id_dict = self.database_manager.query_db("SELECT rig_id FROM Rigs WHERE rig_name = ?",(rig_name,))
            if len(rig_id_dict) == 0:
                self.error_window = Error_window("No rigs exist for this account. Please save a rig first.")
            else:
                rig_id = rig_id_dict[0]["rig_id"]
                light_ids = self.database_manager.query_db("SELECT light_id from Lights_in_rigs WHERE rig_id = ?",(rig_id,))
                fixtures = []
                for light_id_dict in light_ids:
                    fixtures.append(self.database_manager.query_db("SELECT light_type,xpos,ypos,start_channel,fixture_number FROM Lights WHERE light_id=?",(light_id_dict["light_id"],))[0])
                self.light_display.open_rig(fixtures,rig_id)
                self.close()

    def delete_pressed(self):
        rig_name = self.drop_down.currentText()
        if rig_name is None:
            self.error_window = Error_window("No rig was selected. Please try again")
        else:
            self.database_manager.query_db("DELETE FROM Rigs WHERE rig_name = ?",(rig_name,))
        self.close()

    def keyPressEvent(self,e):
        if e.key() == Qt.Key_Return:
            self.open_pressed()
