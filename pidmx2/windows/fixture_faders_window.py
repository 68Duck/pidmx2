from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

class Fixture_faders_window(QWidget,uic.loadUiType(os.path.join("ui","fixture_faders_window.ui"))[0]):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Fixture Faders Window")
        self.initUI()

    def initUI(self):
        self.sliders = []
        for i in range(24):
            self.create_fader(fader_number=(i+1),x=(500//11+100)*((i%12)+1),y=100 if i<12 else 550,start_value=0)

    def create_fader(self,fader_number,x,y,start_value):
        self.dict = {}
        self.slider = QSlider(Qt.Vertical,self)
        self.slider.setMinimum(0)
        self.slider.setMaximum(255)
        self.slider.setValue(start_value)
        self.slider.setGeometry(30,40,30,250)
        self.slider.move(x,y)
        self.slider.setStyleSheet("QSlider::handle {background-color: white;}")
        self.slider.setStyleSheet("QSlider::handle {background-color: #292C34;}")
        self.dict["slider"] = self.slider

        self.select_button = QPushButton("Toggle",self)
        self.select_button.setText("Select")
        self.select_button.setFixedWidth(120)
        self.select_button.setFixedHeight(25)
        self.select_button.move(x-45,y+270)
        self.select_button.clicked.connect(self.select_button_pressed)
        self.select_button.setCheckable(True)
        font = self.select_button.font()
        font.setPointSize(12)
        self.select_button.setFont(font)
        self.select_button.setStyleSheet("border: 1px solid white;border-radius: 5px;background-color: #292C34;color: white;")
        self.dict["select_button"] = self.select_button

        self.new_label = QLabel(self,wordWrap=True)
        self.new_label.setText("Fixture" + str(fader_number))
        self.new_label.setStyleSheet("background-color:red;")
        self.new_label.move(x-40,y+310)
        self.new_label.setAlignment(Qt.AlignCenter)
        self.new_label.setFixedWidth(110)
        font = self.new_label.font()
        font.setPointSize(12)
        self.new_label.setFont(font)
        self.dict["label"] = self.new_label

        self.text_box = QLineEdit(self)
        self.text_box.move(x-45,y+340)
        self.text_box.setPlaceholderText("Intensity value")
        self.text_box.setAlignment(Qt.AlignCenter)
        self.text_box.setFixedWidth(120)
        self.text_box.setFixedHeight(30)
        font = self.text_box.font()
        font.setPointSize(12)
        self.text_box.setFont(font)
        self.text_box.setStyleSheet("border: 2px solid white; border-radius:5px;")
        self.text_box.setText(str(start_value))
        self.dict["text_box"] = self.text_box

        self.sliders.append(self.dict)


    def select_button_pressed(self):
        select_button = self.sender()
        if select_button.isChecked():
            select_button.setStyleSheet("border: 1px solid white;border-radius: 5px;background-color: yellow;color: black;")
        else:
            select_button.setStyleSheet("border: 1px solid white;border-radius: 5px;background-color: #292C34;color: white;")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Fixture_faders_window()
    win.show()
    sys.exit(app.exec_())
