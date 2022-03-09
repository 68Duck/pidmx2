from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys

from windows.open_stage_window import Open_stage_window
from windows.save_stage_window import Save_stage_window

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
                        self.errorWindow = ErrorWindow("The bar letter is invalid. Please try again")
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

class Bar(object):
    def __init__(self,bar_letter,x,y,width,height,is_horizontal,stage_creator_window):
        self.pos = (x,y)
        self.width = width
        self.height = height
        self.name = bar_letter
        self.is_horizontal = is_horizontal
        self.stage_creator_window = stage_creator_window
        self.selected = False
        self.points = []
        self.createShapes()

    def createShapes(self):
        self.bar = QLabel(self.stage_creator_window)
        x,y = self.pos
        self.bar.move(x,y)
        self.bar.setStyleSheet("background-color:white; border: 1px solid white;")
        self.bar.setFixedSize(self.width,self.height)
        if self.is_horizontal:
            self.label = self.create_bar_label(x+self.width+50,y+self.height//2-25)
        else:
            self.label = self.create_bar_label(x-25+self.width//2,y-75)

    def create_bar_label(self,x,y):
        label = QLabel(self.stage_creator_window)
        label.move(int(x),int(y))
        label.setFixedSize(50,50)
        label.setStyleSheet("background-color:white; border: 1px solid white;font-size: 30px;")
        label.setText(self.name)
        label.setAlignment(Qt.AlignCenter)
        return label

    def show(self):
        self.bar.show()
        self.label.show()

    def hide(self):
        self.bar.hide()
        self.label.hide()
        for point in self.points:
            point.hide()

    def check_if_clicked(self,xpos,ypos):
        x,y = self.pos
        if xpos>x and xpos<x+self.width:
            if ypos>y and ypos<y+self.height:
                return True
        return False

    def set_selected(self,selected):
        self.selected = selected
        if selected:
            x,y = self.pos
            width = self.width
            height = self.height
            self.p0 = Point(x,y,self,[1,0,0,1])
            self.p1 = Point(x+width/2,y,self,[0,0,0,1])
            self.p2 = Point(x+width,y,self,[1,1,0,0])
            self.p3 = Point(x,y+height/2,self,[1,0,0,0])
            self.p4 = Point(x+width,y+height/2,self,[0,1,0,0])
            self.p5 = Point(x,y+height,self,[0,0,1,1])
            self.p6 = Point(x+width/2,y+height,self,[0,0,1,0])
            self.p7 = Point(x+width,y+height,self,[0,1,1,0])
            self.points = []
            for i in range(8):
                self.points.append(getattr(self,f"p{i}"))

        else:
            for point in self.points:
                point.hide()

    def swapPointsTopAndBottom(self):
        for point in self.points:
            if point.position[0]:
                point.position[0] = 0
                point.position[2] = 1
            elif point.position[2]:
                point.position[0] = 1
                point.position[2] = 0

    def swapPointsLeftAndRight(self):
        for point in self.points:
            if point.position[1]:
                point.position[1] = 0
                point.position[3] = 1
            elif point.position[3]:
                point.position[1] = 1
                point.position[3] = 0

    def points_moved(self,position,point):
        self.bar.hide()
        self.label.hide()
        top = position[0]
        right = position[1]
        bottom = position[2]
        left = position[3]
        x,y = self.pos
        if top:
            dy = y-point.y
            y = point.y
            self.height += dy
            if self.height < 0:
                self.height = abs(self.height)
                y = y-self.height
                point.swapTB()
        if left:
            dx = x-point.x
            x = point.x
            self.width += dx
            if self.width < 0:
                self.width = abs(self.width)
                x = x - self.width
                point.swapLR()
        if bottom:
            self.height = point.y - y
            if self.height < 0:
                self.height = abs(self.height)
                y=point.y
                point.swapTB()
        if right:
            self.width = point.x - x
            if self.width < 0:
                self.width = abs(self.width)
                x = point.x
                point.swapLR()
        self.pos = (x,y)
        self.set_selected(False) #so hides all current points
        self.set_selected(True) #so creats new points
        self.createShapes()
        self.bar.show()
        self.label.show()

    def set_position(self,pos):
        self.pos = pos
        self.label.hide()
        self.bar.hide()
        self.createShapes()
        self.set_selected(False) #so hides all current points
        self.set_selected(True) #so creats new points
        self.bar.show()
        self.label.show()

    def get_stage_creator_window(self):
        return self.stage_creator_window

    def get_x(self):
        return self.pos[0]

    def get_y(self):
        return self.pos[1]

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_horizontal(self):
        return self.is_horizontal

    def get_bar_name(self):
        return self.name

class Point(object):
    def __init__(self,x,y,bar,position):
        self.position = position  #positions is an array length 4 representing [top,right,bottom,left]
        self.x = x
        self.y = y
        self.bar = bar
        self.width,self.height = [10,10]
        self.createShape()

    def createShape(self):
        self.label = QLabel(self.bar.get_stage_creator_window())
        self.label.move(self.x-self.width//2,self.y-self.height//2)
        self.label.setFixedSize(self.width,self.height)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color:white;border: 2px solid lightgrey; border-radius:100%;")
        self.label.show()

    def hide(self):
        self.label.hide()

    def show(self):
        self.label.show()

    def check_if_clicked(self,xpos,ypos):
        if xpos>self.x-self.width//2 and xpos<self.x+self.width:
            if ypos>self.y-self.height//2 and ypos<self.y+self.height:
                return True #as in the bar clickable range
        return False

    def set_position(self,x=False,y=False):
        if x is not False:
            self.x = x
        if y is not False:
            self.y = y
        self.label.hide()
        # self.createShape()
        self.bar.points_moved(self.position,self)

    def swapLR(self):
        if self.position[1]:
            self.position[1] = 0
            self.position[3] = 1
        elif self.position[3]:
            self.position[1] = 1
            self.position[3] = 0

    def swapTB(self):
        if self.position[0]:
            self.position[0] = 0
            self.position[2] = 1
        elif self.position[2]:
            self.position[0] = 1
            self.position[2] = 0

class Rectangle(object):
    def __init__(self,stage_creator_window,x,y,width,height,side_width = 5):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.side_width = side_width
        self.stage_creator_window = stage_creator_window
        self.shapes = self.create_shapes()

    def create_shapes(self):
        self.side1 = self.create_side(self.x,self.y,self.width,self.side_width)
        self.side2 = self.create_side(self.x,self.y,self.side_width,self.height)
        self.side3 = self.create_side(self.x+self.width,self.y,self.side_width,self.height)
        self.side4 = self.create_side(self.x,self.y+self.height,self.width+self.side_width,self.side_width)
        return [self.side1,self.side2,self.side3,self.side4]

    def create_side(self,x,y,width,height):
        self.side = QLabel(self.stage_creator_window)
        self.side.move(x,y)
        self.side.setFixedSize(width,height)
        self.side.setStyleSheet("background-color:white")
        self.side.show()
        return self.side

    def hide(self):
        for shape in self.shapes:
            shape.hide()

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height
