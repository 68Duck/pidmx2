from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.error_window import Error_window
from windows.message_window import Message_window
from dict_factory import dict_factory

class Record_playback_window(QMainWindow,uic.loadUiType(os.path.join("windows/ui","record_playback_window.ui"))[0]):
    def __init__(self,light_display,database_manager):
        super().__init__()
        self.setupUi(self)
        self.light_display = light_display
        self.database_manager = database_manager
        self.setWindowTitle("Record Playback Window")
        self.show()
        self.initUI()

    def initUI(self):
        self.save_button.clicked.connect(self.save_pressed)
        self.cancel_button.clicked.connect(self.cancel_pressed)
        self.save_name_input.setFocus()
        rig_id = self.light_display.get_rig_id()
        if rig_id is None:
            self.close()
            self.error_window = Error_window("No rig is open. Please open a rig before opening a playback")

    def save_pressed(self):
        rig_id = self.light_display.get_rig_id()
        save_name = self.save_name_input.text()
        if save_name == "":
            self.error_window = Error_window("Please enter a name for the rig")
            return
        results = self.database_manager.query_db("SELECT playback_name FROM Playbacks WHERE rig_id = ? AND playback_name = ?",(rig_id,save_name))
        if len(results) > 0:
            self.error_window = Error_window("There is already a playback with that name")
            return

        con = self.database_manager.get_db()
        con.execute("BEGIN")
        con.row_factory = dict_factory
        con.execute("INSERT INTO Playbacks(rig_id,playback_name) VALUES(?,?)",(rig_id,save_name))
        playback_id = con.execute("SELECT playback_id FROM Playbacks WHERE playback_name = ?",(save_name,)).fetchall()
        if playback_id is None:
            raise Exception("Playback id could not be found")
        if rig_id is None:
            raise Exception("Rig id could not be found")

        fixtures = self.light_display.get_fixtures()
        channel_values = []
        light_effects = []
        for fixture in fixtures:
            if fixture is not None:
                light_id = con.execute("SELECT light_id FROM Lights WHERE light_type = ? AND start_channel = ? AND xpos = ? and ypos = ?",(fixture.get_light_type(),fixture.get_channel_number(),fixture.get_x(),fixture.get_y())).fetchall()
                light_id = light_id[0]["light_id"]
                light_effects.append({"effects":fixture.get_effects(),"light_id":light_id})
                for i,channel in enumerate(fixture.get_channels()):
                    channel_values.append({"channel_number":i+fixture.get_channel_number(),"channel_value":channel[1]})
        for channel_value in channel_values:
            con.execute("INSERT INTO Channel_values(channel_number,channel_value) VALUES(?,?)",(channel_value["channel_number"],channel_value["channel_value"]))
            channel_values_id = con.execute("SELECT channel_values_id FROM Channel_values WHERE channel_number = ? AND channel_value = ?",(channel_value["channel_number"],channel_value["channel_value"])).fetchall()
            con.execute("INSERT INTO Playbacked(playback_id,channel_values_id) VALUES(?,?)",(int(playback_id[0]["playback_id"]),int(channel_values_id[0]["channel_values_id"])))
        for effect in light_effects:
            for effect_name, effect_value in effect["effects"].items():
                con.execute("INSERT INTO Light_effects(light_id,effect_name,effect_value) VALUES (?,?,?)",(effect["light_id"],effect_name,effect_value))
                light_effects_id = con.execute("SELECT light_effects_id FROM Light_effects WHERE light_id = ? AND effect_name = ? AND effect_value = ? ",(effect["light_id"],effect_name,effect_value)).fetchall()
                print(light_effects_id)
                con.execute("INSERT INTO Playback_effects(playback_id,light_effects_id) VALUES(?,?)",(int(playback_id[0]["playback_id"]),light_effects_id[0]["light_effects_id"]))
        con.commit()
        self.message_window = Message_window(f"The playback was saved as {save_name}")
        self.close()

    def cancel_pressed(self):
        self.close()

    def keyPressEvent(self,e):
        if e.key() == Qt.Key_Return:
            self.save_pressed()
