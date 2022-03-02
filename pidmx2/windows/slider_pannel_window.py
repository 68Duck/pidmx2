from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

class Slider_pannel_window(QWidget,uic.loadUiType(os.path.join("windows/ui","slider_pannel_window.ui"))[0]):
    def __init__(self,light,light_display):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Slider Pannel Window")
        self.light = light
        self.light_display = light_display
        self.channels_names = [channel[0] for channel in self.light.get_channels()]
        self.initUI()

    def initUI(self):
        self.sliders = []
        self.setGeometry(0,0,max(480,min(1900,100+150*len(self.channels_names))),550 if len(self.channels_names)<=12 else 1080)
        if len(self.channels_names) > 24:
            raise Exception("There cannot be more than 24 channels (yet)")
            return
        for i,channel in enumerate(self.channels_names):
            self.create_fader(x=100+150*(i if i < 12 else i-12),y=100 if i < 12 else 550,start_value=self.light.get_channels()[i][1],channel_name=channel)

        self.duplicate_fixture_button.clicked.connect(self.duplicate_fixture_button_pressed)
        self.move_fixture_button.clicked.connect(self.move_fixture_button_pressed)
        self.remove_fixture_button.clicked.connect(self.remove_fixture_button_pressed)


    def duplicate_fixture_button_pressed(self):
        pass

    def move_fixture_button_pressed(self):
        pass

    def remove_fixture_button_pressed(self):
        pass


    def create_fader(self,x,y,start_value,channel_name):
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
        new_label.setText(channel_name)
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
            self.channels_changed()

    def get_channel_values(self):
        channel_values = []
        for s in self.sliders:
            label = s["label"]
            channel_name = label.text()
            spin_box = s["spin_box"]
            value = spin_box.value()
            channel_values.append([channel_name,value])
        return channel_values

    def channels_changed(self):
        self.light.set_channels(self.get_channel_values())
        self.light_display.update_universe_from_fixtures()

    def select_button_pressed(self):
        select_button = self.sender()
        if select_button.isChecked():
            select_button.setStyleSheet("border: 1px solid white;border-radius: 5px;background-color: yellow;color: black;")
        else:
            select_button.setStyleSheet("border: 1px solid white;border-radius: 5px;background-color: #292C34;color: white;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Slider_pannel_window()
    win.show()
    sys.exit(app.exec_())
