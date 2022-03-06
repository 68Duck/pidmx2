from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

class Fixture_faders_window(QWidget,uic.loadUiType(os.path.join("windows/ui","fixture_faders_window.ui"))[0]):
    def __init__(self,light_display):
        super().__init__()
        self.setupUi(self)
        self.light_display = light_display
        self.setWindowTitle("Fixture Faders Window")
        self.initUI()

    def initUI(self):
        self.changing_channels = True
        self.faders = []
        for i in range(24):
            self.create_fader(fader_number=(i+1),x=(500//11+100)*((i%12)+1),y=100 if i<12 else 550,start_value=0)

    def update_faders(self,fixtures):
        for i,fixture in enumerate(fixtures):
            if fixture is not None:
                self.changing_channels = False
                self.faders[i]["slider"].setStyleSheet("QSlider::handle {background-color: white;}")
                self.faders[i]["label"].setStyleSheet("background-color:#292C34;")
                self.faders[i]["label"].setText(str(fixture.get_channel_number()))
                self.faders[i]["spin_box"].setValue(fixture.get_intensity())
                self.faders[i]["slider"].setValue(fixture.get_intensity())
                self.changing_channels = True
            else:
                self.changing_channels = False
                self.faders[i]["slider"].setStyleSheet("QSlider::handle {background-color: #292C34;}")
                self.faders[i]["label"].setStyleSheet("background-color:red;")
                self.faders[i]["label"].setText("Fixture" + str(i+1))
                self.faders[i]["spin_box"].setValue(0)
                self.faders[i]["slider"].setValue(0)
                self.changing_channels = True

    def create_fader(self,fader_number,x,y,start_value):
        dict = {}
        slider = QSlider(Qt.Vertical,self)
        slider.setMinimum(0)
        slider.setMaximum(255)
        slider.setValue(start_value)
        slider.setGeometry(30,40,30,250)
        slider.move(x,y)
        # slider.setStyleSheet("QSlider::handle {background-color: white;}")
        slider.setStyleSheet("QSlider::handle {background-color: #292C34;}")
        slider.valueChanged[int].connect(self.slider_changed_value)
        dict["slider"] = slider

        select_button = QPushButton("Toggle",self)
        select_button.setText("Select")
        select_button.setFixedWidth(120)
        select_button.setFixedHeight(25)
        select_button.move(x-45,y+270)
        select_button.clicked.connect(self.select_button_pressed)
        select_button.setCheckable(True)
        font = select_button.font()
        font.setPointSize(12)
        select_button.setFont(font)
        select_button.setStyleSheet("border: 1px solid white;border-radius: 5px;background-color: #292C34;color: white;")
        select_button.number = fader_number
        dict["select_button"] = select_button

        new_label = QLabel(self,wordWrap=True)
        new_label.setText("Fixture" + str(fader_number))
        new_label.setStyleSheet("background-color:red;")
        new_label.move(x-40,y+310)
        new_label.setAlignment(Qt.AlignCenter)
        new_label.setFixedWidth(110)
        font = new_label.font()
        font.setPointSize(12)
        new_label.setFont(font)
        dict["label"] = new_label

        spin_box = QSpinBox(self)
        spin_box.move(x-45,y+340)
        spin_box.setMinimum(0)
        spin_box.setMaximum(255)
        spin_box.setValue(0)
        spin_box.setAlignment(Qt.AlignCenter)
        spin_box.setFixedWidth(120)
        spin_box.setFixedHeight(30)
        font = spin_box.font()
        font.setPointSize(12)
        spin_box.setFont(font)
        spin_box.setStyleSheet("border: 1px solid white; border-radius:5px;")
        spin_box.valueChanged.connect(self.spin_box_changed_value)
        dict["spin_box"] = spin_box

        self.faders.append(dict)

    def faders_changed(self):
        intensities = [fader["spin_box"].value() for fader in self.faders]
        if self.changing_channels:
            self.light_display.update_intensities(intensities)


    def spin_box_changed_value(self):
        spin_box = self.sender()
        s = None
        for s in self.faders:
            if s["spin_box"] == spin_box:
                s["slider"].setValue(spin_box.value())
                record = s
        if s is None:
            raise Exception("Spin box could not be found")

    def slider_changed_value(self):
        slider = self.sender()
        s = None
        for s in self.faders:
            if s["slider"] == slider:
                s["spin_box"].setValue(slider.value())
                record = s
        if s is None:
            raise Exception("Slider could not be found")
        else:
            self.faders_changed()


    def select_button_pressed(self):
        select_button = self.sender()
        if self.light_display.get_fixtures()[select_button.number-1] is not None:
            self.light_display.toggle_fixture(select_button.number)
            if select_button.isChecked():
                select_button.setStyleSheet("border: 1px solid white;border-radius: 5px;background-color: yellow;color: black;")
            else:
                select_button.setStyleSheet("border: 1px solid white;border-radius: 5px;background-color: #292C34;color: white;")

    def update_select_buttons(self,fixtures):
        for fixture in fixtures:
            if fixture is not None:
                select_button = self.faders[fixture.get_fixture_number()-1]["select_button"]
                if fixture.is_selected():
                    select_button.setChecked(True)
                    select_button.setStyleSheet("border: 1px solid white;border-radius: 5px;background-color: yellow;color: black;")
                else:
                    select_button.setChecked(False)
                    select_button.setStyleSheet("border: 1px solid white;border-radius: 5px;background-color: #292C34;color: white;")
