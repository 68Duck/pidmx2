from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.save_window import Save_window
from windows.message_window import Message_window
from windows.error_window import Error_window
from dict_factory import dict_factory

class Save_sequence_window(Save_window):
    def __init__(self,sequence_window,light_display,database_manager):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Save Sequence Window")
        self.light_display = light_display
        self.sequence_window = sequence_window
        self.database_manager = database_manager
        self.initUI()

    def initUI(self):
        self.save_button.clicked.connect(self.save_pressed)
        self.cancel_button.clicked.connect(self.close)

    def save_pressed(self):
        rig_id = self.light_display.get_rig_id()
        if rig_id is None:
            self.error_window = Error_window("There is no rig open. Please open a rig before trying to save a sequence")
            return
        save_name = self.save_name_input.text()
        if save_name == "":
            self.error_window = Error_window("Please enter a name for the sequence")
            return

        results = self.database_manager.query_db("SELECT sequence_id FROM Sequences WHERE sequence_name = ? AND rig_id = ?",(save_name,rig_id))
        if len(results) > 0:
            self.error_window = Error_window("There is already a sequence with that name")
            return

        con = self.database_manager.get_db()
        con.execute("BEGIN")
        con.row_factory = dict_factory
        con.execute("INSERT INTO Sequences(sequence_name,rig_id) VALUES(?,?)",(save_name,rig_id))
        sequence_id = con.execute("SELECT sequence_id FROM Sequences WHERE sequence_name = ? AND rig_id = ?",(save_name,rig_id)).fetchall()
        sequence_id = sequence_id[0]["sequence_id"]
        if sequence_id is None:
            raise Exception("Sequence id could not be found")

        self.sequence_window.set_sequence_id(sequence_id)
        sequence_fixtures = self.sequence_window.get_sequence_fixtures()
        for f in sequence_fixtures:
            fixture = f.get_parent_fixture()
            light_id = con.execute("SELECT light_id FROM Lights WHERE light_type = ? AND start_channel = ? AND xpos = ? and ypos = ?",(fixture.get_light_type(),fixture.get_channel_number(),fixture.get_x(),fixture.get_y())).fetchall()[0]["light_id"]
            con.execute("INSERT INTO Lights_in_sequence(sequence_id,light_id) VALUES(?,?)",(sequence_id,light_id))

        con.commit()
        self.message_window = Message_window(f"The sequence was saved as {save_name}")
        self.close()

    def keyPressEvent(self,e):
        if e.key() == Qt.Key_Return:
            self.save_pressed()
