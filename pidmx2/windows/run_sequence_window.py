from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.error_window import Error_window

class Run_sequence_window(QMainWindow,uic.loadUiType(os.path.join("windows/ui","run_sequence_window.ui"))[0]):
    def __init__(self,light_display,database_manager,light_display_window):
        super().__init__()
        self.setupUi(self)
        self.light_display = light_display
        self.database_manager = database_manager
        self.light_display_window = light_display_window
        self.setWindowTitle("Run Sequence Window")
        self.initUI()

    def initUI(self):
        self.run_button.clicked.connect(self.run_pressed)
        rig_id = self.light_display.get_rig_id()
        if rig_id is None:
            self.error_window = Error_window("There is not rig open. Please open a rig before trying to run a sequence")
            self.close()
            return
        else:
            self.show()
        sequences = self.database_manager.query_db("SELECT sequence_name FROM Sequences WHERE rig_id = ?",(rig_id,))
        for sequence in sequences:
            self.drop_down.addItem(sequence["sequence_name"])

    def run_pressed(self):
        sequence_name = self.drop_down.currentText()
        rig_id = self.light_display.get_rig_id()
        if sequence_name is None:
            self.error_window = Error_window("No sequence was selected. Please try again")
        else:
            sequence_id_dict = self.database_manager.query_db("SELECT sequence_id FROM Sequences WHERE sequence_name = ? and rig_id = ?",(sequence_name,rig_id))
            sequence_id = sequence_id_dict[0]["sequence_id"]
            sequence_playbacks = self.database_manager.query_db("SELECT s.playback_id,s.time_delay FROM Sequence_playbacks s JOIN Playbacks p ON p.playback_id = s.playback_id WHERE s.sequence_id = ? ORDER BY p.playback_name ",(sequence_id,))
            loop = self.loop_check_box.isChecked()
            step = self.step_check_box.isChecked()
            self.light_display_window.run_sequence(sequence_playbacks,loop=loop,step=step)
        self.close()
