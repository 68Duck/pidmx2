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
        self.initUI()

    def initUI(self):
        self.mode_selection_action.triggered.connect(self.mode_selection_pressed)
        self.patch_action.triggered.connect(self.patch_pressed)

    def patch_pressed(self):
        self.light_display.run_patching_window()

    def add_fixture(self,x,y,light_type,fixture_number,channel_number):
        result = self.light_display.add_fixture(x,y,light_type,fixture_number,channel_number,self)
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
                    self.add_fixture(x,y,self.new_light_type,self.new_fixture_number,self.new_channel_number)
                    self.placing_light = False
                    return 1

        return super(Light_display_window, self).eventFilter(source, event)


    def place_fixture(self,light_type,fixture_number,channel_number):
        self.new_light_type = light_type
        self.new_fixture_number = fixture_number
        self.new_channel_number = channel_number
        self.placing_light = True


    def mode_selection_pressed(self):
        self.light_display.run_mode_selection_window()
        self.close()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Light_display_window()
    win.show()
    sys.exit(app.exec_())
