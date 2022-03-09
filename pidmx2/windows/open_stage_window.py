from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys
from windows.open_window import Open_window


class Open_stage_window(Open_window):
    def __init__(self,light_display,database_manager,stage_creator_window):
        super().__init__()
        self.setupUi(self)
        self.database_manager = database_manager
        self.light_display = light_display
        self.stage_creator_window = stage_creator_window
        self.setWindowTitle("Open Stage Window")
        self.initUI()

    def initUI(self):
        self.open_button.clicked.connect(self.open_pressed)
        self.delete_button.clicked.connect(self.delete_pressed)
        account_id = self.light_display.get_account_id()
        location_ids = self.database_manager.query_db("SELECT location_id FROM Locations_in_account WHERE account_id = ?",(account_id,))
        saved_locations = []
        for id in location_ids:
            saved_locations.append(self.database_manager.query_db("SELECT location_name FROM Locations WHERE location_id = ?",(id["location_id"],))[0])
        for location in saved_locations:
            self.drop_down.addItem(location["location_name"])

    def open_pressed(self):
        location_name = self.drop_down.currentText()
        if location_name is None:
            self.error_window = Error_window("No location was selected. Please try again")
        else:
            location_id_dict = self.database_manager.query_db("SELECT location_id FROM Locations WHERE location_name = ?",(location_name,))
            if len(location_id_dict) == 0:
                self.error_window = Error_window("No locations exist for this account. Please save a location first.")
            else:
                location_id = location_id_dict[0]["location_id"]
                bars_ids = self.database_manager.query_db("SELECT bars_id from Bars_in_locations WHERE location_id = ?",(location_id,))
                rectangles_ids = self.database_manager.query_db("SELECT rectangles_id from Rectangles_in_locations WHERE location_id = ?",(location_id,))
                bars = []
                rectangles = []
                for bars_id_dict in bars_ids:
                    bars.append(self.database_manager.query_db("SELECT width,height,xpos,ypos,is_horizontal,bar_name FROM Bars WHERE bars_id=?",(bars_id_dict["bars_id"],))[0])
                for rectangles_id_dict in rectangles_ids:
                    rectangles.append(self.database_manager.query_db("SELECT width,height,xpos,ypos FROM Rectangles WHERE rectangles_id=?",(rectangles_id_dict["rectangles_id"],))[0])

                self.stage_creator_window.open_location(bars,rectangles)
                self.close()

    def delete_pressed(self):
        location_name = self.drop_down.currentText()
        if location_name is None:
            self.error_window = Error_window("No location was selected. Please try again")
        else:
            self.database_manager.query_db("DELETE FROM Locations WHERE location_name = ?",(location_name,))
        self.close()

    def keyPressEvent(self,e):
        if e.key() == Qt.Key_Return:
            self.open_pressed()
