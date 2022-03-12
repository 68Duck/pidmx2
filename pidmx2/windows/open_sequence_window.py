from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.open_window import Open_window
from windows.error_window import Error_window

class Open_sequence_window(Open_window):
    def __init__(self,light_display,database_manager,sequence_window):
        super().__init__()
        self.database_manager = database_manager
        self.sequence_window = sequence_window
        self.light_display = light_display
        self.setWindowTitle("Open Sequence Window")
        self.initUI()

    def initUI(self):
        rig_id = self.light_display.get_rig_id()
        self.open_button.clicked.connect(self.open_pressed)
        self.delete_button.clicked.connect(self.delete_pressed)
        saved_sequences = self.database_manager.query_db("SELECT sequence_name FROM Sequences WHERE rig_id = ?",(rig_id,))
        for sequence in saved_sequences:
            self.drop_down.addItem(sequence["sequence_name"])

    def open_pressed(self):
        rig_id = self.light_display.get_rig_id()
        sequence_name = self.drop_down.currentText()
        if sequence_name is None:
            self.error_window = Error_window("No sequence was selected. Please try again")
        else:
            sequence_id_dict = self.database_manager.query_db("SELECT sequence_id FROM Sequences WHERE sequence_name = ? and rig_id = ?",(sequence_name,rig_id))
            if len(sequence_id_dict) == 0:
                self.error_window = Error_window("No sequences exist for this rig. Please save a sequence first.")
            else:
                sequence_id = sequence_id_dict[0]["sequence_id"]
                light_ids = self.database_manager.query_db("SELECT light_id from Lights_in_sequence WHERE sequence_id = ?",(sequence_id,))
                # sequence_playbacks = self.database_manager.query_db("SELECT playback_id,time_delay FROM Sequence_playbacks WHERE sequence_id = ?",(sequence_id,))
                sequence_playbacks = self.database_manager.query_db("SELECT s.playback_id,s.time_delay FROM Sequence_playbacks s JOIN Playbacks p ON p.playback_id = s.playback_id WHERE s.sequence_id = ? ORDER BY p.playback_name ",(sequence_id,))

                self.sequence_window.open_sequence(light_ids,sequence_id,sequence_playbacks)
                self.close()

    def delete_pressed(self):
        qm = QMessageBox
        result = qm.question(self,'Delete Sequence?', "Are you sure you want to delete the sequence?", qm.Yes | qm.No)
        if result == qm.Yes:
            rig_id = self.light_display.get_rig_id()
            sequence_name = self.drop_down.currentText()
            if sequence_name is None:
                self.error_window = Error_window("No rig was selected. Please try again")
            else:
                self.database_manager.query_db("DELETE FROM sequences WHERE sequence_name = ? AND rig_id = ?",(sequence_name,rig_id))
            self.close()

    def keyPressEvent(self,e):
        if e.key() == Qt.Key_Return:
            self.open_pressed()
