from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

class Effects_window(QWidget,uic.loadUiType(os.path.join("windows/ui","effects_window.ui"))[0]):
    def __init__(self,light_display):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Effects Window")
        self.light_display = light_display
        self.effects = ["Chaser","Rainbow"]
        self.running_effects = {"Chaser":0,"Rainbow":0}
        self.initUI()

    def initUI(self):
        self.sliders = []
        self.setGeometry(0,0,min(100+150*len(self.effects),1900),550 if len(self.effects)<=12 else 1080)
        if len(self.effects) > 24:
            raise Exception("There cannot be more than 24 effects")
            return
        for i,effect in enumerate(self.effects):
            self.create_fader(x=100+150*(i if i < 12 else i-12),y=100 if i < 12 else 550,start_value=0,effect_name=effect)

    def create_fader(self,x,y,start_value,effect_name):
        dict = {}
        slider = QSlider(Qt.Vertical,self)
        slider.setMinimum(0)
        slider.setMaximum(255)
        slider.setValue(start_value)
        slider.setGeometry(30,40,30,250)
        slider.move(x,y)
        slider.setStyleSheet("QSlider::handle {background-color: white;}")
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
        dict["select_button"] = select_button

        new_label = QLabel(self,wordWrap=True)
        new_label.setText(effect_name)
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
        spin_box.setValue(start_value)
        spin_box.setAlignment(Qt.AlignCenter)
        spin_box.setFixedWidth(120)
        spin_box.setFixedHeight(30)
        font = spin_box.font()
        font.setPointSize(12)
        spin_box.setFont(font)
        spin_box.setStyleSheet("border: 1px solid white; border-radius:5px;")
        spin_box.valueChanged.connect(self.spin_box_changed_value)
        dict["spin_box"] = spin_box

        self.sliders.append(dict)

    def spin_box_changed_value(self):
        spin_box = self.sender()
        s = None
        for s in self.sliders:
            if s["spin_box"] == spin_box:
                s["slider"].setValue(spin_box.value())
                record = s
        if s is None:
            raise Exception("Spin box could not be found")

    def slider_changed_value(self):
        slider = self.sender()
        s = None
        for s in self.sliders:
            if s["slider"] == slider:
                s["spin_box"].setValue(slider.value())
                record = s
        if s is None:
            raise Exception("Slider could not be found")
        else:
            self.update_running_effects()
            self.update_fixtures_effects()

    def update_running_effects(self):
        for dict in self.sliders:
            effect_name = dict["label"].text()
            effect_value = dict["slider"].value()
            effect_selected = dict["select_button"].isChecked()
            if effect_selected:
                self.running_effects[effect_name] = effect_value
            else:
                self.running_effects[effect_name] = 0

    def update_fixtures_effects(self):
        fixtures = self.light_display.get_fixtures()
        selected_fixtures = []
        no_fixtures = 0
        for fixture in fixtures:
            if fixture is not None:
                if fixture.is_selected():
                    no_fixtures += 1
                    fixture.set_effects(self.running_effects)
        counter = -1
        for f in fixtures:
            if f is not None:
                if f.is_selected():
                    counter += 1
                    if no_fixtures == 1:
                        chase = [0,1]
                    else:
                        chase = [0]*no_fixtures
                        chase[counter] = 1
                    f.set_chase(chase)

    def select_button_pressed(self):
        select_button = self.sender()
        if select_button.isChecked():
            select_button.setStyleSheet("border: 1px solid white;border-radius: 5px;background-color: yellow;color: black;")
        else:
            select_button.setStyleSheet("border: 1px solid white;border-radius: 5px;background-color: #292C34;color: white;")
        self.update_running_effects()
        self.update_fixtures_effects()
