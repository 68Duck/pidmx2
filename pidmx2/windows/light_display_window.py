from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.error_window import Error_window
from windows.message_window import Message_window
from windows.open_stage_window import Open_stage_window
from bar_and_rectangle_classes import Rectangle,Bar

class Light_display_window(QMainWindow,uic.loadUiType(os.path.join("windows/ui","light_display_window.ui"))[0]):
    def __init__(self,light_display,username,database_manager):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Light Display Window")
        self.light_display = light_display
        self.username = username
        self.database_manager = database_manager
        self.setMouseTracking(True)
        self.placing_light = False
        self.selecting_lights = False
        self.bars = []
        self.rectangles = []
        self.opening_playback_ids = []
        self.looping_sequence = False
        self.running_sequence = False
        self.sequence_playbacks = None
        self.stepping_sequence = False
        self.current_playback = None
        self.initUI()

    def initUI(self):
        self.mode_selection_action.triggered.connect(self.mode_selection_pressed)
        self.patch_action.triggered.connect(self.patch_pressed)
        self.fixture_faders_action.triggered.connect(self.fixture_faders_pressed)
        self.open_rig_action.triggered.connect(self.open_rig_pressed)
        self.save_rig_action.triggered.connect(self.save_rig_pressed)
        self.select_lights_action.triggered.connect(self.select_lights_pressed)
        self.select_all_lights_action.triggered.connect(self.select_all_lights_pressed)
        self.select_light_type_action.triggered.connect(self.select_light_type_pressed)
        self.effects_action.triggered.connect(self.effects_pressed)
        self.open_playback_action.triggered.connect(self.open_playback_pressed)
        self.record_playback_action.triggered.connect(self.record_playback_pressed)
        self.stage_creator_action.triggered.connect(self.stage_creator_pressed)
        self.open_stage_action.triggered.connect(self.open_stage_pressed)
        self.sequence_action.triggered.connect(self.sequence_pressed)
        self.run_sequence_action.triggered.connect(self.run_sequence_pressed)
        self.stop_sequence_action.triggered.connect(self.stop_sequence_pressed)
        self.blackout_button.clicked.connect(self.blackout_pressed)

    def blackout_pressed(self):
        self.light_display.set_blackout(self.blackout_button.isChecked())

    def run_sequence_pressed(self):
        self.light_display.run_run_sequence_window()

    def set_looping_sequence(self,looping_sequence):
        self.looping_sequence = looping_sequence

    def stop_sequence_pressed(self):
        self.stop_sequence()
        self.message_window = Message_window("The sequence was stopped")

    def stop_sequence(self):
        self.looping_sequence = False
        self.running_sequence = False
        self.stepping_sequence = False
        self.opening_playback_ids = []

    def run_sequence(self,sequence_playbacks,loop=False,step=False):
        self.looping_sequence = loop
        self.running_sequence = True
        self.sequence_playbacks = sequence_playbacks

        if step:
            self.stepping_sequence = True
            self.current_playback = 0
            for playback in self.sequence_playbacks:
                self.opening_playback_ids.append(playback["playback_id"])
            self.open_playback()
        else:
            self.stepping_sequence = False
            QTimer.singleShot(1,self.iterate_sequence)

    def iterate_sequence(self):
        current_time_delay = 0
        for playback in self.sequence_playbacks:
            self.opening_playback_ids.append(playback["playback_id"])
            time_delay = playback["time_delay"]
            current_time_delay += time_delay
            QTimer.singleShot(current_time_delay*1000,self.open_playback) #calls the open playback function after time_delay milliseconds
        if self.looping_sequence:
            QTimer.singleShot(current_time_delay*1000,self.iterate_sequence)
        else:
            QTimer.singleShot((1+current_time_delay)*1000,self.stop_sequence)


    def open_playback(self):
        if self.running_sequence:
            if self.stepping_sequence:
                playback_id = self.opening_playback_ids[self.current_playback]
            else:
                playback_id = self.opening_playback_ids.pop(0)
            channel_values_ids = self.database_manager.query_db("SELECT channel_values_id from Playbacked WHERE playback_id = ?",(playback_id,))
            channel_values = []
            for channel_value_dict in channel_values_ids:
                channel_values.append(self.database_manager.query_db("SELECT channel_number,channel_value FROM Channel_values WHERE channel_values_id=?",(channel_value_dict["channel_values_id"],))[0])
            self.light_display.open_playback(channel_values,[])


    def sequence_pressed(self):
        self.light_display.run_sequence_window_function()

    def open_stage_pressed(self):
        self.open_stage_window = Open_stage_window(self.light_display,self.database_manager,self)
        self.open_stage_window.show()

    def open_location_by_location_naem(self,location_name): #Spelt wrong? Where is this called from?
        location_id_dict = self.database_manager.query_db("SELECT location_id FROM Locations WHERE location_name = ?",(location_name,))
        if len(location_id_dict) == 0:
            raise Exception("No location with that name exists")
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
            self.open_location(bars,rectangles)


    def open_location(self,bars,rectangles):
        for bar in self.bars:
            bar.hide()
        for rectangle in self.rectangles:
            rectangle.hide()
        self.bars = []
        self.rectangles = []
        for bar in bars:
            self.new_bar = Bar(bar["bar_name"],bar["xpos"],bar["ypos"],bar["width"],bar["height"],bar["is_horizontal"],self)
            self.new_bar.show()
            self.bars.append(self.new_bar)
        for rectangle in rectangles:
            self.new_rectangle = Rectangle(self,rectangle["xpos"],rectangle["ypos"],rectangle["width"],rectangle["height"])
            self.rectangles.append(self.new_rectangle)

    def stage_creator_pressed(self):
        self.light_display.run_stage_creator_window()

    def record_playback_pressed(self):
        self.light_display.run_record_playback_window()

    def open_playback_pressed(self):
        self.light_display.run_open_playback_window()

    def effects_pressed(self):
        self.light_display.run_effects_window()

    def select_all_lights_pressed(self):
        for fixture in self.light_display.get_fixtures():
            if fixture is not None:
                if not fixture.is_selected():
                    fixture.toggle_selected()

    def select_light_type_pressed(self):
        self.light_display.run_select_light_type_window()

    def select_lights_pressed(self):
        self.selecting_lights = self.select_lights_action.isChecked()

    def save_rig_pressed(self):
        self.light_display.run_save_rig_window()

    def open_rig_pressed(self):
        self.light_display.run_open_rig_window()

    def fixture_faders_pressed(self):
        self.light_display.run_fixture_faders_window()

    def patch_pressed(self):
        self.light_display.run_patching_window()

    def add_fixture(self,x,y,light_type,fixture_number,channel_number,copy=False,channels=None):
        result = self.light_display.add_fixture(x,y,light_type,fixture_number,channel_number,self,copy,channels)
        if result is True:
            pass
        else:
            self.error_window = Error_window(result)

    def eventFilter(self,source,event):
        if self.placing_light:
            if event.type() == QEvent.MouseMove:
                x = event.x()
                y = event.y()
                if x!=0 and y!=0:
                    self.light_display.preview_fixture(x,y,self.new_light_type,self)
                    return 1
            if event.type() == QEvent.MouseButtonPress:
                if event.buttons() == Qt.LeftButton:
                    x = event.x()
                    y = event.y()
                    self.add_fixture(x,y,self.new_light_type,self.new_fixture_number,self.new_channel_number,self.placing_copy_light,self.placing_light_channels)
                    self.placing_light = self.light_display.setup_next_light_to_place()
                    return 1
        else: #so checking if a light was cliked
            if source == self: #only want to detect mouse clicks on the light display window
                if event.type() == QEvent.MouseButtonPress:
                    if event.buttons() == Qt.LeftButton:
                        if self.selecting_lights:
                            x = event.x()
                            y = event.y()
                            self.light_display.check_for_light_select(x,y)
                        else:
                            x = event.x()
                            y = event.y()
                            self.light_display.check_for_light_click(x,y)
        if (event.type() == QEvent.KeyPress):
            key = event.key()
            if self.stepping_sequence:
                if key == Qt.Key_Space:
                    if self.looping_sequence:
                        self.current_playback = (self.current_playback+1)%len(self.opening_playback_ids)
                    else:
                        if self.current_playback+1 == len(self.opening_playback_ids):
                            self.stop_sequence()
                        else:
                            self.current_playback += 1
                    self.open_playback()
                    return 1 #stops double trigger
                elif key == Qt.Key_Backspace:
                    if self.looping_sequence:
                        self.current_playback = (self.current_playback-1)%len(self.opening_playback_ids)
                    else:
                        if self.current_playback - 1 < 0:
                            self.stop_sequence()
                        else:
                            self.current_playback -= 1
                    self.open_playback()
                    return 1 #stops double trigger



        return super(Light_display_window, self).eventFilter(source, event)


    def place_fixture(self,light_type,fixture_number,channel_number,copy=False,channels=None):
        self.new_light_type = light_type
        self.new_fixture_number = fixture_number
        self.new_channel_number = channel_number
        self.placing_light = True
        self.placing_copy_light = copy
        self.placing_light_channels = channels


    def mode_selection_pressed(self):
        self.light_display.run_mode_selection_window()
        self.close()
