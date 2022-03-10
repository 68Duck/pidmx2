from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*

class Bar(object):
    def __init__(self,bar_letter,x,y,width,height,is_horizontal,display_window):
        self.pos = (x,y)
        self.width = width
        self.height = height
        self.name = bar_letter
        self.is_horizontal = is_horizontal
        self.display_window = display_window
        self.selected = False
        self.points = []
        self.createShapes()

    def createShapes(self):
        self.bar = QLabel(self.display_window)
        x,y = self.pos
        self.bar.move(x,y)
        self.bar.setStyleSheet("background-color:white; border: 1px solid white;")
        self.bar.setFixedSize(self.width,self.height)
        if self.is_horizontal:
            self.label = self.create_bar_label(x+self.width+50,y+self.height//2-25)
        else:
            self.label = self.create_bar_label(x-25+self.width//2,y-75)

    def create_bar_label(self,x,y):
        label = QLabel(self.display_window)
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

    def get_display_window(self):
        return self.display_window

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
        self.label = QLabel(self.bar.get_display_window())
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
    def __init__(self,display_window,x,y,width,height,side_width = 5):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.side_width = side_width
        self.display_window = display_window
        self.shapes = self.create_shapes()

    def create_shapes(self):
        self.side1 = self.create_side(self.x,self.y,self.width,self.side_width)
        self.side2 = self.create_side(self.x,self.y,self.side_width,self.height)
        self.side3 = self.create_side(self.x+self.width,self.y,self.side_width,self.height)
        self.side4 = self.create_side(self.x,self.y+self.height,self.width+self.side_width,self.side_width)
        return [self.side1,self.side2,self.side3,self.side4]

    def create_side(self,x,y,width,height):
        self.side = QLabel(self.display_window)
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
