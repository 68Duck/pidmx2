from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.open_window import Open_window
from windows.error_window import Error_window

class Open_playback_window(Open_window):
    def __init__(self,light_display,database_manager):
        super().__init__()
        self.database_manager = database_manager
        self.light_display = light_display
        self.setWindowTitle("Open Playback Window")
        self.show()
        self.initUI()

    def initUI(self):
        self.open_button.clicked.connect(self.open_pressed)
        self.delete_button.clicked.connect(self.delete_pressed)
        account_id = self.light_display.get_account_id()
        rig_id = self.light_display.get_rig_id()
        if rig_id is None:
            self.close()
            self.error_window = Error_window("No rig is open. Please open a rig before opening a playback")
        else:
            playback_names = self.database_manager.query_db("SELECT playback_name FROM Playbacks WHERE rig_id = ?",(rig_id,))
            for playback_name in playback_names:
                self.drop_down.addItem(playback_name["playback_name"])

    def open_pressed(self):
        playback_name = self.drop_down.currentText()
        if playback_name is None:
            self.error_window = Error_window("No playback was selected. Please try again")
        else:
            playback_id_dict = self.database_manager.query_db("SELECT playback_id FROM Playbacks WHERE playback_name = ?",(playback_name,))
            if len(playback_id_dict) == 0:
                self.error_window = Error_window("No rigs exist for this account. Please save a rig first.")
            else:
                playback_id = playback_id_dict[0]["playback_id"]
                channel_values_ids = self.database_manager.query_db("SELECT channel_values_id from Playbacked WHERE playback_id = ?",(playback_id,))
                channel_values = []
                for channel_value_dict in channel_values_ids:
                    channel_values.append(self.database_manager.query_db("SELECT channel_number,channel_value FROM Channel_values WHERE channel_values_id=?",(channel_value_dict["channel_values_id"],))[0])

                light_effect_ids = self.database_manager.query_db("SELECT light_effects_id FROM Playback_effects WHERE playback_id = ?",(playback_id,))
                light_effects = []
                for light_effect_dict in light_effect_ids:
                    light_effects.append(self.database_manager.query_db("SELECT light_id,effect_name,effect_value FROM Light_effects WHERE light_effects_id = ?",(light_effect_dict["light_effects_id"],))[0])
                self.light_display.open_playback(channel_values,light_effects)
                self.close()

    def delete_pressed(self):
        qm = QMessageBox
        result = qm.question(self,'Delete Playback?', "Are you sure you want to delete the playback?", qm.Yes | qm.No)
        if result == qm.Yes:
            playback_name = self.drop_down.currentText()
            if playback_name is None:
                self.error_window = Error_window("No rig was selected. Please try again")
            else:
                self.database_manager.query_db("DELETE FROM Playbacks WHERE playback_name = ?",(playback_name,))
            self.close()

    def keyPressEvent(self,e):
        if e.key() == Qt.Key_Return:
            self.open_pressed()
