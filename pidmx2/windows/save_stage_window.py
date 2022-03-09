from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.save_window import Save_window
from windows.message_window import Message_window
from dict_factory import dict_factory

class Save_stage_window(Save_window):
    def __init__(self,stage_window,light_display,database_manager):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Save Stage Window")
        self.light_display = light_display
        self.stage_window = stage_window
        self.database_manager = database_manager
        self.initUI()

    def initUI(self):
        self.save_button.clicked.connect(self.save_pressed)
        self.cancel_button.clicked.connect(self.close)

    def save_pressed(self):
        account_id = self.light_display.get_account_id()
        save_name = self.save_name_input.text()
        if save_name == "":
            self.error_window = Error_window("Please enter a name for the location")
            return
        results = self.database_manager.query_db("SELECT l.location_id FROM Locations l JOIN Locations_in_account a ON l.location_id = a.location_id WHERE a.account_id = ? AND l.location_name = ?",(account_id,save_name))
        if len(results) > 0:
            self.error_window = Error_window("There is already a location with that name")
            return

        con = self.database_manager.get_db()
        con.execute("BEGIN")
        con.row_factory = dict_factory
        con.execute("INSERT INTO Locations(location_name) VALUES(?)",(save_name,))
        location_id = con.execute("SELECT location_id FROM Locations WHERE location_name = ?",(save_name,)).fetchall()
        if location_id is None:
            raise Exception("Rig id could not be found")
        if account_id is None:
            raise Exception("Account id could not be found")
        con.execute("INSERT INTO Locations_in_account(account_id,location_id) VALUES(?,?)",(int(account_id),int(location_id[0]["location_id"])))

        bars = self.stage_window.get_bars()
        rectangles = self.stage_window.get_rectangles()
        for bar in bars:
            con.execute("INSERT INTO Bars(width,height,xpos,ypos,is_horizontal,bar_name) VALUES(?,?,?,?,?,?)",(bar.get_width(),bar.get_height(),bar.get_x(),bar.get_y(),bar.get_horizontal(),bar.get_bar_name()))
            bars_id = con.execute("SELECT bars_id FROM Bars WHERE width = ? AND height = ? AND xpos = ? and ypos = ? AND is_horizontal = ? AND bar_name = ?",(bar.get_width(),bar.get_height(),bar.get_x(),bar.get_y(),bar.get_horizontal(),bar.get_bar_name())).fetchall()
            con.execute("INSERT INTO Bars_in_locations(location_id,bars_id) VALUES(?,?)",(int(location_id[0]["location_id"]),int(bars_id[0]["bars_id"])))
        for rectangle in rectangles:
            con.execute("INSERT INTO Rectangles(width,height,xpos,ypos) VALUES(?,?,?,?)",(rectangle.get_width(),rectangle.get_height(),rectangle.get_x(),rectangle.get_y()))
            rectangles_id = con.execute("SELECT rectangles_id FROM Rectangles WHERE width = ? AND height = ? AND xpos = ? AND ypos = ?",(rectangle.get_width(),rectangle.get_height(),rectangle.get_x(),rectangle.get_y())).fetchall()
            con.execute("INSERT INTO Rectangles_in_locations(location_id,rectangles_id) VALUES(?,?)",(int(location_id[0]["location_id"]),int(rectangles_id[0]["rectangles_id"])))
        con.commit()
        self.message_window = Message_window(f"The location was saved as {save_name}")
        self.close()

    def keyPressEvent(self,e):
        if e.key() == Qt.Key_Return:
            self.save_pressed()
