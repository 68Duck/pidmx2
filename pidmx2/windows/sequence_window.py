from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.error_window import Error_window
from windows.save_sequence_window import Save_sequence_window
from windows.record_sequence_playback_window import Record_sequence_playback_window
from windows.open_sequence_window import Open_sequence_window
from windows.edit_sequence_window import Edit_sequence_window

class Sequence_window(QMainWindow,uic.loadUiType(os.path.join("windows/ui","sequence_window.ui"))[0]):
    def __init__(self,light_display,database_manager):
        super().__init__()
        self.setupUi(self)
        self.light_display = light_display
        self.database_manager = database_manager
        self.sequence_fixtures = []
        self.sequence_playbacks = []
        self.chosen_colour = [0,0,0]
        self.choosing_colour = False
        self.sequence_id = None
        self.current_playback = None
        self.opening_playback_id = None
        self.setWindowTitle("Sequence Window")
        self.initUI()


    def initUI(self):
        self.add_light_action.triggered.connect(self.add_light_pressed)
        self.add_all_lights_action.triggered.connect(self.add_all_lights_pressed)
        self.choose_colour_action.triggered.connect(self.choose_colour_pressed)
        self.replace_colour_action.triggered.connect(self.replace_colour_pressed)
        self.colour_mode_action.triggered.connect(self.colour_mode_pressed)
        self.save_sequence_action.triggered.connect(self.save_sequence_pressed)
        self.open_sequence_action.triggered.connect(self.open_sequence_pressed)
        self.edit_sequence_action.triggered.connect(self.edit_sequence_pressed)
        self.record_playback_action.triggered.connect(self.record_sequence_playback_pressed)
        self.next_playback_button.clicked.connect(self.next_playback_pressed)
        self.previous_playback_button.clicked.connect(self.previous_playback_pressed)
        if self.light_display.get_rig_id() is None:
            self.error_window = Error_window("There is no rig opened. Please try openeing a rig before creating a sequence")
            self.close()
            return
        elif len([fixture for fixture in self.light_display.get_fixtures() if fixture is not None]) == 0:
            self.error_window = Error_window("There are no lights in the opened rig. Please try openeing a rig with lights before creating a sequence")
            self.close()
            return
        else:
            self.show()

    def add_light_pressed(self):
        fixtures = self.light_display.get_fixtures()
        fixture_names = [str(fixture.get_light_type())+str(fixture.get_channel_number()) for fixture in fixtures if fixture is not None and str(fixture.get_light_type())+str(fixture.get_channel_number()) not in [str(f.get_light_type())+str(f.get_channel_number()) for f in self.sequence_fixtures]]
        if len(fixture_names) > 0:
            fixture_name, ok_pressed = QInputDialog.getItem(self, "Enter Light Name:","Light", fixture_names, 0, False)
            if ok_pressed:
                fixture = [fixture for fixture in fixtures if fixture is not None and fixture_name == str(fixture.get_light_type())+str(fixture.get_channel_number())][0]
                self.new_fixture = fixture.generate_new_light(fixture.get_x(),fixture.get_y(),fixture.get_channel_number(),fixture.get_fixture_number(),self,False,fixture)
                self.sequence_fixtures.append(self.new_fixture)
        else:
            self.error_window = Error_window("There are no lights left to place")

    def add_all_lights_pressed(self):
        for fixture in self.light_display.get_fixtures():
            if fixture is not None:
                if str(fixture.get_light_type())+str(fixture.get_channel_number()) not in [str(f.get_light_type())+str(f.get_channel_number()) for f in self.sequence_fixtures]:
                    self.new_fixture = fixture.generate_new_light(fixture.get_x(),fixture.get_y(),fixture.get_channel_number(),fixture.get_fixture_number(),self,False,fixture)
                    self.sequence_fixtures.append(self.new_fixture)
        if len(self.sequence_fixtures) == 0:
            self.error_window = Error_window("There are no lights left to place")

    def open_sequence(self,light_ids,sequence_id,sequence_playbacks):
        for fixture in self.sequence_fixtures: #close previous sequence
            fixture.hide()
        self.sequence_fixtures = []
        self.sequence_playbacks = []

        self.sequence_id = sequence_id
        for light_id_dict in light_ids:
            light_id = light_id_dict["light_id"]
            for fixture in self.light_display.get_fixtures():
                if fixture is not None:
                    if light_id == self.database_manager.query_db("SELECT light_id FROM Lights WHERE light_type = ? AND start_channel = ? AND xpos = ? and ypos = ?",(fixture.get_light_type(),fixture.get_channel_number(),fixture.get_x(),fixture.get_y()))[0]["light_id"]:
                        self.new_fixture = fixture.generate_new_light(fixture.get_x(),fixture.get_y(),fixture.get_channel_number(),fixture.get_fixture_number(),self,False,fixture)
                        self.sequence_fixtures.append(self.new_fixture)

        self.update_sequence_playbacks(sequence_playbacks)

    def update_sequence_playbacks(self,sequence_playbacks):
        self.sequence_playbacks = sequence_playbacks
        self.current_playback = -1
        self.open_next_playback()

    def open_next_playback(self):
        if len(self.sequence_playbacks) == 0:
            print("There are no playbacks")
            return False
        else:
            self.current_playback = (self.current_playback + 1)%len(self.sequence_playbacks)
            self.opening_playback_id = self.sequence_playbacks[self.current_playback]["playback_id"]
            time_delay = self.sequence_playbacks[self.current_playback]["time_delay"]
            self.open_playback()
            return True

    def open_previous_playback(self):
        if len(self.sequence_playbacks) == 0:
            print("There are no playbacks")
            return False
        else:
            self.current_playback = (self.current_playback - 1)%len(self.sequence_playbacks)
            self.opening_playback_id = self.sequence_playbacks[self.current_playback]["playback_id"]
            self.open_playback()
            return True

    def open_playback(self):
        playback_id = self.opening_playback_id
        channel_values_ids = self.database_manager.query_db("SELECT channel_values_id from Playbacked WHERE playback_id = ?",(playback_id,))
        channel_values = []
        for channel_value_dict in channel_values_ids:
            channel_values.append(self.database_manager.query_db("SELECT channel_number,channel_value FROM Channel_values WHERE channel_values_id=?",(channel_value_dict["channel_values_id"],))[0])

        for channel in channel_values:
            for fixture in self.sequence_fixtures:
                if fixture.get_channel_number() <= channel["channel_number"] and fixture.get_channel_number() + len(fixture.get_channels()) > channel["channel_number"]:
                    channel_index = channel["channel_number"] - fixture.get_channel_number()  #should work since both one indexed
                    fixture.set_channel(channel_index,channel["channel_value"],change_colour = True)
        for fixture in self.sequence_fixtures:
            fixture.update_display()
            fixture.update_parent()
        self.light_display.update_universe_from_fixtures()

    def get_sequence_fixtures(self):
        return self.sequence_fixtures

    def get_sequence_playbacks(self):
        return self.sequence_playbacks

    def get_sequence_id(self):
        return self.sequence_id

    def set_sequence_id(self,sequence_id):
        self.sequence_id = sequence_id

    def eventFilter(self,source,event):
        if source == self: #only want to detect mouse clicks on the light display window
            if event.type() == QEvent.MouseButtonPress:
                if event.buttons() == Qt.LeftButton:
                    if self.choosing_colour:
                        x = event.x()
                        y = event.y()
                        for fixture in self.sequence_fixtures:
                            if fixture.check_for_click(x,y):
                                r,g,b = self.chosen_colour
                                fixture.set_colour(r,g,b)
                                fixture.set_intensity(max(self.chosen_colour))
                                fixture.update_parent()
                        self.light_display.update_universe_from_fixtures()
                    else:
                        x = event.x()
                        y = event.y()
                        for fixture in self.sequence_fixtures:
                            if fixture.check_for_click(x,y):
                                colour = QColorDialog.getColor()
                                if colour.isValid():
                                    red = colour.red()
                                    green = colour.green()
                                    blue = colour.blue()
                                    fixture.set_colour(red,green,blue)
                                    fixture.set_intensity(max(red,green,blue))
                                    fixture.update_parent()
                                else:
                                    self.error_window = Error_window("The colour you selected is not valid. Please try again")
                        self.light_display.update_universe_from_fixtures()


        return super(Sequence_window, self).eventFilter(source, event)

    def previous_playback_pressed(self):
        self.open_previous_playback()

    def next_playback_pressed(self):
        self.open_next_playback()

    def choose_colour_pressed(self):
        colour = QColorDialog.getColor()
        if colour.isValid():
            red = colour.red()
            green = colour.green()
            blue = colour.blue()
            self.chosen_colour = [red,green,blue]
            self.choosing_colour = True
            self.colour_mode_action.setChecked(True)
        else:
            self.error_window = Error_window("The colour you selected is not valid. Please try again")


    def replace_colour_pressed(self):
        colour = QColorDialog.getColor()
        if colour.isValid():
            red = colour.red()
            green = colour.green()
            blue = colour.blue()
            colour_to_replace = [red,green,blue]
            colour = QColorDialog.getColor()
            if colour.isValid():
                red = colour.red()
                green = colour.green()
                blue = colour.blue()
                for fixture in self.sequence_fixtures:
                    if fixture.get_colour() == colour_to_replace:
                        fixture.set_colour(red,green,blue)
                        fixture.set_intensity(max(red,green,blue))
                        fixture.update_parent()
                self.light_display.update_universe_from_fixtures()


    def colour_mode_pressed(self):
        self.choosing_colour = self.colour_mode_action.isChecked()

    def save_sequence_pressed(self):
        self.save_sequence_window = Save_sequence_window(self,self.light_display,self.database_manager)
        self.save_sequence_window.show()

    def open_sequence_pressed(self):
        self.open_sequence_window = Open_sequence_window(self.light_display,self.database_manager,self)
        self.open_sequence_window.show()

    def edit_sequence_pressed(self):
        self.edit_sequence_window = Edit_sequence_window(self.light_display,self.database_manager,self)
        #not shown since done in window for validation purposes

    def record_sequence_playback_pressed(self):
        self.record_sequence_playback_window = Record_sequence_playback_window(self.light_display,self.database_manager,self)
        # self.record_sequence_playback_window.show() #not shown since done in class for not opening possiblity
