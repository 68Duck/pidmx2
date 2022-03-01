from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.error_window import Error_window

class Patching_window(QMainWindow,uic.loadUiType(os.path.join("windows/ui","patching_window.ui"))[0]):
    def __init__(self,light_display):
        super().__init__()
        self.setupUi(self)
        self.light_display = light_display
        self.setWindowTitle("Patching Window")
        self.initUI()

    def initUI(self):
        self.submit_button.clicked.connect(self.submit_pressed)
        self.patch_one_light_radio.clicked.connect(self.patch_one_light_radio_pressed)
        self.patch_multiple_lights_radio.clicked.connect(self.patch_multiple_lights_radio_pressed)
        self.patch_one_light_radio_pressed()
        self.add_lights_to_dropdown()
        self.setup_channels_tab()
        self.setup_fixtures_tab()

    def patch_one_light_radio_pressed(self):
        self.multiple_lights_widget.hide()

    def patch_multiple_lights_radio_pressed(self):
        self.multiple_lights_widget.show()

    def setup_channels_tab(self):
        self.channel_labels = []
        start_x = 10
        start_y = 10
        x_gap = 30
        y_gap = 15
        no_x = 32
        no_y = 16
        width = 28
        height = 13
        x_coords = []
        y_coords = []
        for i in range(no_x):
            x_coords.append(start_x+x_gap*i)
        for i in range(no_y):
            y_coords.append(start_y+y_gap*i)

        for i in range(no_x):
            for j in range(no_y):
                self.new_channel_label = self.create_channel_label(x_coords[i],y_coords[j],j*no_x+i+1,width,height)
                self.channel_labels.append(self.new_channel_label)

    def setup_fixtures_tab(self):
        self.fixtues_labels = []
        start_x = 10
        start_y = 10
        x_gap = 70
        y_gap = 30
        no_x = 6
        no_y = 4
        width = 50
        height = 20
        x_coords = []
        y_coords = []
        for i in range(no_x):
            x_coords.append(start_x+x_gap*i)
        for i in range(no_y):
            y_coords.append(start_y+y_gap*i)

        for i in range(no_x):
            for j in range(no_y):
                self.new_fixture_label = self.create_fixture_label(x_coords[i],y_coords[j],j*no_x+i+1,width,height)
                self.fixtues_labels.append(self.new_fixture_label)

    def create_fixture_label(self,move_x,move_y,number,width,height):
        self.new_label = QLabel(self.fixtures_tab)
        self.new_label.setText(str(number))
        self.new_label.setFixedSize(width,height)
        self.new_label.move(move_x,move_y)
        if self.light_display.check_if_fixture_free(number):
            self.new_label.setStyleSheet("background-color: lightgrey;color: black; border: 2px solid green; font-size: 11px;")
        else:
            self.new_label.setStyleSheet("background-color: lightgrey;color: black; border: 2px solid red; font-size: 11px;")

        self.new_label.setAlignment(Qt.AlignCenter)
        self.new_label.show()
        return self.new_label

    def create_channel_label(self,move_x,move_y,number,width,height):
        self.new_label = QLabel(self.channels_tab)
        self.new_label.setText(str(number))
        self.new_label.setFixedSize(width,height)
        self.new_label.move(move_x,move_y)
        if self.light_display.check_if_channel_free(number):
            self.new_label.setStyleSheet("background-color: lightgrey;color: black; border: 2px solid green; font-size: 11px;")
        else:
            self.new_label.setStyleSheet("background-color: lightgrey;color: black; border: 2px solid red; font-size: 11px;")

        self.new_label.setAlignment(Qt.AlignCenter)
        self.new_label.show()
        return self.new_label

    def add_lights_to_dropdown(self):
        for light_type in self.light_display.get_light_types():
            self.light_type_dropdown.addItem(light_type)

    def keyPressEvent(self,e): #on the enter key being pressed, call the submit_pressed function
        if e.key() == Qt.Key_Return:
            self.submit_pressed()

    def submit_pressed(self):
        channel_number = self.channel_number_input.value()
        fixture_number = self.fixture_number_input.value()
        light_type = self.light_type_dropdown.currentText()
        if self.patch_one_light_radio.isChecked():
            result = self.light_display.check_new_fixture(light_type,fixture_number,channel_number)
            if result is True:
                self.light_display.place_fixture(light_type,fixture_number,channel_number)
                self.close()
            else:
                self.error_window = Error_window(result)
        elif self.patch_multiple_lights_radio.isChecked():
            number_of_lights = self.number_of_fixtures_input.value()
            channel_gap = self.channel_gap_input.value()
            for i in range(number_of_lights):
                result = self.light_display.check_new_fixture(light_type,fixture_number+i,channel_number+i*channel_gap)
        else:
            raise Exception("No radio is pressed") #The program should never reach here
