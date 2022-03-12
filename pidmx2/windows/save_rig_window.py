from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.save_window import Save_window
from windows.error_window import Error_window
from windows.message_window import Message_window
from dict_factory import dict_factory


class Save_rig_window(Save_window):
    def __init__(self,light_display,database_manager):
        super().__init__()
        self.light_display = light_display
        self.database_manager = database_manager
        self.setWindowTitle("Save Rig Window")
        self.initUI()

    def initUI(self):
        self.save_button.clicked.connect(self.save_pressed)
        self.cancel_button.clicked.connect(self.cancel_pressed)

    def save_pressed(self):
        account_id = self.light_display.get_account_id()
        save_name = self.save_name_input.text()
        if save_name == "":
            self.error_window = Error_window("Please enter a name for the rig")
            return
        results = self.database_manager.query_db("SELECT r.rig_name FROM Rigs r JOIN Rigs_in_account a ON a.rig_id = r.rig_id WHERE a.account_id = ? AND r.rig_name = ?",(account_id,save_name))
        if len(results) > 0:
            self.error_window = Error_window("There is already a rig with that name")
            return

        con = self.database_manager.get_db()
        con.execute("BEGIN")
        con.row_factory = dict_factory
        con.execute("INSERT INTO Rigs(rig_name) VALUES(?)",(save_name,))
        rig_id = con.execute("SELECT rig_id FROM Rigs WHERE rig_name = ?",(save_name,)).fetchall()
        if rig_id is None:
            raise Exception("Rig id could not be found")
        if account_id is None:
            raise Exception("Account id could not be found")
        con.execute("INSERT INTO Rigs_in_account(account_id,rig_id) VALUES(?,?)",(int(account_id),int(rig_id[0]["rig_id"])))

        fixtures = self.light_display.get_fixtures()
        copy_lights = self.light_display.get_copy_lights()
        for fixture in fixtures:
            if fixture is not None:
                con.execute("INSERT INTO Lights(light_type,xpos,ypos,start_channel,fixture_number) VALUES(?,?,?,?,?)",(fixture.get_light_type(),fixture.get_x(),fixture.get_y(),fixture.get_channel_number(),fixture.get_fixture_number()))
                light_id = con.execute("SELECT light_id FROM Lights WHERE light_type = ? AND start_channel = ? AND xpos = ? and ypos = ?",(fixture.get_light_type(),fixture.get_channel_number(),fixture.get_x(),fixture.get_y())).fetchall()
                con.execute("INSERT INTO Lights_in_rigs(rig_id,light_id) VALUES(?,?)",(int(rig_id[0]["rig_id"]),int(light_id[0]["light_id"])))
        for copy_light in copy_lights:
            con.execute("INSERT INTO Lights(light_type,xpos,ypos,start_channel,fixture_number) VALUES(?,?,?,?,?)",(copy_light.get_light_type(),copy_light.get_x(),copy_light.get_y(),copy_light.get_channel_number(),copy_light.get_fixture_number()))
            light_id = con.execute("SELECT light_id FROM Lights WHERE light_type = ? AND start_channel = ? AND xpos = ? AND ypos = ?",(copy_light.get_light_type(),copy_light.get_channel_number(),copy_light.get_x(),copy_light.get_y())).fetchall()
            con.execute("INSERT INTO Lights_in_rigs(rig_id,light_id) VALUES(?,?)",(int(rig_id[0]["rig_id"]),int(light_id[0]["light_id"])))
        con.commit()
        self.light_display.set_rig_id(rig_id[0]["rig_id"])
        self.message_window = Message_window(f"The rig was saved as {save_name}")
        self.close()

    def cancel_pressed(self):
        self.close()

    def keyPressEvent(self,e):
        if e.key() == Qt.Key_Return:
            self.save_pressed()
