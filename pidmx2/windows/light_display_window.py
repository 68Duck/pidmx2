from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.error_window import Error_window

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
