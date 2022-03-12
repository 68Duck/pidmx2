from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.error_window import Error_window
from windows.message_window import Message_window
from dict_factory import dict_factory

class Record_sequence_playback_window(QMainWindow,uic.loadUiType(os.path.join("windows/ui","record_playback_window.ui"))[0]):
    def __init__(self,light_display,database_manager,sequence_window):
        super().__init__()
        self.setupUi(self)
        self.light_display = light_display
        self.database_manager = database_manager
        self.sequence_window = sequence_window
        self.setWindowTitle("Record Sequence Playback Window")
        self.initUI()

    def initUI(self):
        self.save_button.clicked.connect(self.save_pressed)
        self.cancel_button.clicked.connect(self.cancel_pressed)
        self.name_label.setText("Time Delay (s):")
        self.save_name_input.setFocus()
        sequence_id = self.sequence_window.get_sequence_id()
        if sequence_id is None:
            self.error_window = Error_window("No sequence is open. Please open a sequence before saving a playback")
            self.close()
        else:
            self.show()

    def save_pressed(self):
        sequence_id = self.sequence_window.get_sequence_id()
        time_delay = self.save_name_input.text()
        if time_delay == "":
            self.error_window = Error_window("Please enter a time delay")
            return
        try:
            time_delay = float(time_delay)
        except:
            self.error_window = Error_window("The time delay must be a number. Please try again")
            return
        sequence_playbacks = self.sequence_window.get_sequence_playbacks()
        rig_id = self.light_display.get_rig_id()
        if rig_id is None:
            self.error_window = Error_window("There is no rig open. Please open a rig before trying to save a sequence")
            return

        save_name = "sequence" + str(sequence_id) + "no" + str(len(sequence_playbacks)+1)
        results = self.database_manager.query_db("SELECT playback_id FROM Playbacks WHERE rig_id = ? AND playback_name = ?",(rig_id,save_name))
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

        con.execute("INSERT INTO Sequence_playbacks(sequence_id,playback_id,time_delay) VALUES (?,?,?)",(sequence_id,playback_id[0]["playback_id"],time_delay))
        sequence_playback_id = con.execute("SELECT sequence_playback_id FROM Sequence_playbacks WHERE sequence_id = ? AND playback_id = ?",(sequence_id,playback_id[0]["playback_id"])).fetchall()
        if sequence_playback_id is None:
            raise Exception("Sequence playback id could not be found")

        sequence_fixtures = self.sequence_window.get_sequence_fixtures()
        channel_values = []
        for f in sequence_fixtures:
            fixture = f.get_parent_fixture()
            for i,channel in enumerate(fixture.get_channels()):
                channel_values.append({"channel_number":i+fixture.get_channel_number(),"channel_value":channel[1]})
        for channel_value in channel_values:
            con.execute("INSERT INTO Channel_values(channel_number,channel_value) VALUES(?,?)",(channel_value["channel_number"],channel_value["channel_value"]))
            channel_values_id = con.execute("SELECT channel_values_id FROM Channel_values WHERE channel_number = ? AND channel_value = ?",(channel_value["channel_number"],channel_value["channel_value"])).fetchall()
            con.execute("INSERT INTO Playbacked(playback_id,channel_values_id) VALUES(?,?)",(int(playback_id[0]["playback_id"]),int(channel_values_id[0]["channel_values_id"])))

        con.commit()
        sequence_playbacks = self.database_manager.query_db("SELECT s.playback_id,s.time_delay FROM Sequence_playbacks s JOIN Playbacks p ON p.playback_id = s.playback_id WHERE s.sequence_id = ? ORDER BY p.playback_name ",(sequence_id,))
        self.sequence_window.update_sequence_playbacks(sequence_playbacks)
        self.message_window = Message_window(f"The playback number {len(sequence_playbacks)} was saved")
        self.close()

    def cancel_pressed(self):
        self.close()

    def keyPressEvent(self,e):
        if e.key() == Qt.Key_Return:
            self.save_pressed()
