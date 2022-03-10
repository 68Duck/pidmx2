from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.open_stage_window import Open_stage_window
from windows.save_stage_window import Save_stage_window
from bar_and_rectangle_classes import Rectangle,Bar
from windows.error_window import Error_window

class Stage_creator_window(QMainWindow,uic.loadUiType(os.path.join("windows/ui","stage_creator_window.ui"))[0]):
    def __init__(self,light_display,database_manager):
        super().__init__()
        self.setupUi(self)
        self.light_display = light_display
        self.database_manager = database_manager
        self.setWindowTitle("Stage Creator Window")
        self.placing_bar = False
        self.initUI()

    def initUI(self):
        self.previous_bar_location = None
        self.bars = []
        self.rectangles = []
        self.temp_bar = None
        self.moving_point = None
        self.moving_bar = None
        self.temp_rectangle = None
        self.current_bar_letter = None
        self.creating_horizontal_bar = False
        self.creating_vertical_bar = False
        self.creating_initial_rectangle_point = False
        self.creating_final_rectangle_point = False
        self.changing_bar_size = True
        self.rectangle_label_1.hide()
        self.rectangle_label_2.hide()
        self.add_vertical_action.triggered.connect(self.add_vertical_pressed)
        self.add_horizontal_action.triggered.connect(self.add_horizontal_pressed)
        self.add_stage_rectangle_action.triggered.connect(self.add_stage_rectangle_pressed)
        self.change_bar_size_action.triggered.connect(self.change_bar_size_pressed)
        self.open_location_action.triggered.connect(self.open_location_pressed)
        self.save_stage_layout_action.triggered.connect(self.save_stage_layout_pressed)

    def get_bars(self):
        return self.bars

    def get_rectangles(self):
        return self.rectangles

    def add_stage_rectangle_pressed(self):
        self.creating_initial_rectangle_point = True
        self.rectangle_label_1.show()

    def save_stage_layout_pressed(self):
        self.save_stage_window = Save_stage_window(self,self.light_display,self.database_manager)
        self.save_stage_window.show()

    def open_location_pressed(self):
        self.open_stage_window = Open_stage_window(self.light_display,self.database_manager,self)
        self.open_stage_window.show()

    def change_bar_size_pressed(self):
        self.changing_bar_size = self.change_bar_size_action.isChecked()

    def add_vertical_pressed(self):
        self.add_bar(horizontal=False)

    def add_horizontal_pressed(self):
        self.add_bar(horizontal=True)

    def add_bar(self,horizontal):
        letters = []
        for i in range(26):
            letters.append(chr(65+i))
        letter, okPressed = QInputDialog.getItem(self, "Enter Bar Letter:","Letter:", letters, 0, False)
        if okPressed and letter:
            self.current_bar_letter = letter
            if horizontal:
                self.creating_horizontal_bar = True
            else:
                self.creating_vertical_bar = True

    def place_bar(self):
        self.placing_bar = True
        self.placing_bar_is_horizontal = True

    def eventFilter(self,source,event):
        if event.type() == QEvent.MouseButtonRelease:
            self.moving_point = None
            self.moving_bar = False
        if event.type() == QEvent.MouseButtonPress:
            if event.buttons() == Qt.LeftButton:
                selected = False
                if not self.moving_point:
                    for bar in self.bars:
                        if bar.selected:
                            for point in bar.points:
                                if point.check_if_clicked(event.x(),event.y()):
                                    self.moving_point = point
                                    selected = True
                            if not self.moving_point:
                                if bar.check_if_clicked(event.x(),event.y()):
                                    self.moving_bar = bar
                                    self.previous_bar_location = (event.x(),event.y()) #moves relative to the current location of the mouse
                                    selected = True
                if not selected:
                    for bar in self.bars:
                        bar.set_selected(False)
        if event.type() == QEvent.MouseMove:
            if event.x() != 0 and event.y() != 0:
                if self.moving_point:
                        self.moving_point.set_position(event.x(),event.y())
                if self.moving_bar:
                    dx = event.x() - self.previous_bar_location[0]
                    dy = event.y() - self.previous_bar_location[1]
                    x = self.moving_bar.pos[0] + dx
                    y = self.moving_bar.pos[1] + dy
                    self.moving_bar.set_position((x,y))
                    self.previous_bar_location = (event.x(),event.y())

        if self.changing_bar_size:
            if event.type() == QEvent.MouseButtonPress:
                if event.buttons() == Qt.LeftButton:
                    for bar in self.bars:
                        if bar.check_if_clicked(event.x(),event.y()):
                            bar.set_selected(not bar.selected)
        if self.creating_initial_rectangle_point:
            if event.type() == QEvent.MouseButtonPress:
                if event.buttons() == Qt.LeftButton:
                    if source == self:
                        self.initial_rectangle_x = event.x()
                        self.initial_rectangle_y = event.y()
                        self.creating_initial_rectangle_point = False
                        self.creating_final_rectangle_point = True
                        self.rectangle_label_1.hide()
                        self.rectangle_label_2.show()
        elif self.creating_final_rectangle_point:
            if event.type() == QEvent.MouseMove:
                self.x = event.x()
                self.y = event.y()
                if self.x != 0 and self.y != 0: #gets rid of the random 0's that appear for some reason
                    self.draw_temp_rectangle((self.initial_rectangle_x,self.initial_rectangle_y),(self.x,self.y))
            if event.type() == QEvent.MouseButtonPress:
                if event.buttons() == Qt.LeftButton:
                    self.x = event.x()
                    self.y = event.y()
                    valid = self.create_rectangle()
                    if valid:
                        self.creating_final_rectangle_point = False
                        self.rectangle_label_2.hide()
        if self.creating_horizontal_bar or self.creating_vertical_bar:
            if event.type() == QEvent.MouseMove:
                self.x = event.x()
                self.y = event.y()
                if self.x != 0 and self.y != 0: #gets rid of the random 0's that appear for some reason
                    if self.current_bar_letter is not False:
                        self.preview_bar(self.x,self.y,self.current_bar_letter,horizontal = True if self.creating_horizontal_bar else False)
                        # if source == self:
                        #     print("test2")
                    else:
                        self.error_window = Error_window("The bar letter is invalid. Please try again")
                return 1
            if event.type() == QEvent.MouseButtonPress:
                if event.buttons() == Qt.LeftButton:
                    self.x = event.x()
                    self.y = event.y()
                    self.create_bar()
                    self.creating_horizontal_bar = False
                    self.creating_vertical_bar = False
        return super(Stage_creator_window, self).eventFilter(source, event)

    def preview_bar(self,x,y,bar_name,horizontal):
        if self.temp_bar is not None:
            self.temp_bar.hide()
        if self.creating_vertical_bar or self.creating_horizontal_bar:
            if horizontal:
                self.temp_bar = Bar(bar_name,x,y,900,25,horizontal,self)
            else:
                self.temp_bar = Bar(bar_name,x,y,25,400,horizontal,self)
            self.temp_bar.show()

    def create_bar(self):
        if self.temp_bar is not None:
            self.bars.append(self.temp_bar)
            self.temp_bar = None

    def draw_temp_rectangle(self,point_1,point_2):
        if self.temp_rectangle is not None:
            if self.temp_rectangle not in self.rectangles:
                self.temp_rectangle.hide()
        x0,y0 = point_1
        x1,y1 = point_2
        width = abs(x0-x1)
        height = abs(y0-y1)
        top_left_x = x0 if x0<x1 else x1
        top_left_y = y0 if y0<y1 else y1
        self.temp_rectangle = Rectangle(self,top_left_x,top_left_y,width,height)

    def create_rectangle(self):
        if self.temp_rectangle is not None:
            self.rectangles.append(self.temp_rectangle)
            return True
        return False

    def open_location(self,bars,rectangles):
        for bar in self.bars:
            bar.hide()
        self.bars = []
        for rectangle in self.rectangles:
            rectangle.hide()
        self.rectangles = []
        for bar in bars:
            self.new_bar = Bar(bar["bar_name"],bar["xpos"],bar["ypos"],bar["width"],bar["height"],bar["is_horizontal"],self)
            self.new_bar.show()
            self.bars.append(self.new_bar)
        for rectangle in rectangles:
            self.new_rectangle = Rectangle(self,rectangle["xpos"],rectangle["ypos"],rectangle["width"],rectangle["height"])
            self.rectangles.append(self.new_rectangle)
