from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import math as maths

class Light_type(object):
    def __init__(self,x,y,channel_number,fixture_number,light_display_window,copy):
        self.light_display_window = light_display_window
        self.channel_number = channel_number
        self.fixture_number = fixture_number
        # self.channels = [["channel_name","channel_value"]]
        self.x = x
        self.y = y
        self.copy = copy
        self.intensity = 0
        self.selected = False

    def set_channel(self,channel_number,channel_value):
        if channel_number > len(self.channels):
            raise Exception("Channel out of range")
        else:
            self.channels[channel_number][1] = channel_value
            self.update_display()

    def create_shapes(self): #creates the shapes for each part of the abstraction of the light
        pass

    def move(self): #moves the light to the current x and y position
        pass

    def generate_new_light(self): #creates a new instance of the light
        pass

    def hide(self):
        for shape in self.shapes:
            shape.hide()

    def set_channels(self,channels): #add more validation?
        if len(channels) == len(self.channels):
            self.channels = channels
            self.update_display(change_colour=True)
        else:
            raise Exception("The channels given are not of the same length. Please try again")

    def update_display(self,change_colour=False):
        pass #changes the display to the value of the channels so intensity etc.

    def get_channels(self):
        return self.channels

    def is_copy(self):
        return self.copy is True

    def get_light_type(self):
        return self.light_type

    def get_channel_number(self):
        return self.channel_number

    def get_fixture_number(self):
        return self.fixture_number

    def get_intensity(self):
        return self.intensity

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def is_selected(self):
        return self.selected

    def set_intensity(self,intensity):
        self.intensity = intensity
        self.update_channels_from_intensity()
        self.update_display()

    def update_channels_from_intensity(self):
        pass

    def check_for_click(self,x,y):
        if x>self.x-self.clickable_region[0] and x < self.x+self.clickable_region[1]:
            if y>self.y-self.clickable_region[2] and y<self.y+self.clickable_region[3]:
                return True
        return False

    def toggle_selected(self,update_faders=True):
        self.selected = not self.selected
        if self.selected:
            self.select_shape.show()
        else:
            self.select_shape.hide()
        if update_faders:
            self.light_display_window.light_display.update_fixture_faders_selected_buttons()




class Generic_dimmer(Light_type):
    def __init__(self,x,y,channel_number,fixture_number,light_display_window,copy):
        super().__init__(x,y,channel_number,fixture_number,light_display_window,copy)
        self.channels = [["Intensity",0]]
        self.light_type = "Generic_dimmer"
        self.clickable_region = [0,35,0,75] #in the order left right top bottom from x,y
        if self.light_display_window is not None:
            self.shapes = self.create_shapes()
            self.update_display()

    def create_shapes(self):
        self.border = self.create_shape(self.x,self.y,35,75,border=True)
        self.box = self.create_shape(self.x+5,self.y+5,25,65)
        self.indicator = self.create_shape(self.x+5,self.y,25,20)
        self.select_shape = self.create_select_shape()
        return [self.border,self.box,self.indicator,self.select_shape]

    def create_select_shape(self):
        select_shape = QLabel(self.light_display_window)
        select_shape.move(self.x-5,self.y-5)
        select_shape.setStyleSheet("border: 1px solid orange; background-color:transparent")
        select_shape.setFixedSize(45,85)
        return select_shape

    def move(self):
        self.border.move(self.x,self.y)
        self.box.move(self.x+5,self.y+5)
        self.indicator.move(self.x+5,self.y)

    def create_shape(self,x,y,width,height,border=False):
        self.shape = QLabel(self.light_display_window)
        if border:
            self.shape.setStyleSheet(f'background-color: white;')
        else:
            self.shape.setStyleSheet(f'background-color: black;')
        self.shape.move(x,y)
        self.shape.setFixedSize(width,height)
        self.shape.show()
        return self.shape

    def generate_new_light(self,x,y,channel_number,fixture_number,light_display_window,copy):
        return Generic_dimmer(x,y,channel_number,fixture_number,light_display_window,copy)

    def update_display(self,change_colour=False):
        self.intensity = self.channels[0][1]
        self.indicator.setStyleSheet(f'background-color: rgba(255,255,0,{self.intensity/255});')

    def update_channels_from_intensity(self):
        self.channels[0][1] = self.intensity

class RGBW_light(Light_type):
    def __init__(self,x,y,channel_number,fixture_number,light_display_window,copy):
        super().__init__(x,y,channel_number,fixture_number,light_display_window,copy)
        self.channels = [["Red",0],["Green",0],["Blue",0],["White",0]]
        self.light_type = "RGBW_light"
        self.clickable_region = [40,40,40,40] #in the order left right top bottom from x,y
        self.colour = [0,0,0,0]
        if self.light_display_window is not None:
            self.shapes = self.create_shapes()
            self.move()
            self.update_display()

    def create_shapes(self):
        self.border = self.create_shape(self.x-35,self.y-35,80,80,20)
        for i in range(1,6,1):
            setattr(self,f"circle{i}",self.create_shape(self.x,self.y,10,10,int(10/2),True))
        self.select_shape = self.create_select_shape()
        return [self.border,self.circle1,self.circle2,self.circle3,self.circle4,self.circle5,self.select_shape]

    def create_select_shape(self):
        select_shape = QLabel(self.light_display_window)
        select_shape.move(self.x-40,self.y-40)
        select_shape.setStyleSheet("border: 1px solid orange; background-color:transparent")
        select_shape.setFixedSize(90,90)
        return select_shape


    def move(self):
        self.circle1.move(self.x,self.y)
        self.circle2.move(self.x-20,self.y-20)
        self.circle3.move(self.x-20,self.y+20)
        self.circle4.move(self.x+20,self.y-20)
        self.circle5.move(self.x+20,self.y+20)
        self.border.move(self.x-35,self.y-35)

    def create_shape(self,x,y,width,height,borderWidth,circle = False):
        self.shape = QLabel(self.light_display_window)
        if circle:
            self.shape.borderWidth = borderWidth
            self.shape.setStyleSheet(f'background-color: white; border-radius: {borderWidth}px;border: 3px solid white;')
        else:
            self.shape.setStyleSheet(f'background-color: black; border-radius: {borderWidth}px;border: 3px solid white;')
        self.shape.move(x,y)
        self.shape.setFixedSize(width,height)
        self.shape.show()
        return self.shape

    def generate_new_light(self,x,y,channel_number,fixture_number,light_display_window,copy):
        return RGBW_light(x,y,channel_number,fixture_number,light_display_window,copy)

    def update_display(self,change_colour=False):
        red = self.channels[0][1]
        green = self.channels[1][1]
        blue = self.channels[2][1]
        white = self.channels[3][1]
        if change_colour:
            self.colour = [red,green,blue,white]
        self.intensity = max(red,green,blue,white)
        red = min(255,red+white) #done to incorperate the white into the display but does not affect the real sending of data
        green = min(255,green+white)
        blue = min(255,blue+white)
        for i in range(5):
            self.shapes[1+i].setStyleSheet(f'background-color: rgba({red},{green},{blue},1); border-radius: {self.circle1.borderWidth}px;border: 3px solid rgba({red},{green},{blue},1);')  #all borderwidths should be the same

    def update_channels_from_intensity(self):
        red, green, blue, white = self.colour
        if red > 0:
            r = maths.floor(red/max(red,green,blue,white)*self.intensity)
        else:
            r=0
        if green > 0:
            g = maths.floor(green/max(red,green,blue,white)*self.intensity)
        else:
            g=0
        if blue > 0:
            b = maths.floor(blue/max(red,green,blue,white)*self.intensity)
        else:
            b=0
        if white > 0:
            w = maths.floor(white/max(red,green,blue,white)*self.intensity)
        else:
            w=0
        self.channels[0][1] = r
        self.channels[1][1] = g
        self.channels[2][1] = b
        self.channels[3][1] = self.intensity if max(red,green,blue) == 0 else w


class RGB_light(Light_type):
    def __init__(self,x,y,channel_number,fixture_number,light_display_window,copy):
        super().__init__(x,y,channel_number,fixture_number,light_display_window,copy)
        self.channels = [["Intensity",0],["Red",0],["Green",0],["Blue",0]]
        self.light_type = "RGB_light"
        self.clickable_region = [40,40,40,40] #in the order left right top bottom from x,y
        self.colour = [0,0,0]
        if self.light_display_window is not None:
            self.shapes = self.create_shapes()
            self.move()
            self.update_display()

    def create_shapes(self):
        self.border = self.create_shape(self.x-35,self.y-35,80,80,20)
        for i in range(1,6,1):
            setattr(self,f"circle{i}",self.create_shape(self.x,self.y,10,10,int(10/2),True))
        self.select_shape = self.create_select_shape()
        return [self.border,self.circle1,self.circle2,self.circle3,self.circle4,self.circle5,self.select_shape]

    def create_select_shape(self):
        select_shape = QLabel(self.light_display_window)
        select_shape.move(self.x-40,self.y-40)
        select_shape.setStyleSheet("border: 1px solid orange; background-color:transparent")
        select_shape.setFixedSize(90,90)
        return select_shape

    def move(self):
        self.circle1.move(self.x,self.y)
        self.circle2.move(self.x-20,self.y-20)
        self.circle3.move(self.x-20,self.y+20)
        self.circle4.move(self.x+20,self.y-20)
        self.circle5.move(self.x+20,self.y+20)
        self.border.move(self.x-35,self.y-35)

    def create_shape(self,x,y,width,height,borderWidth,circle = False):
        self.shape = QLabel(self.light_display_window)
        if circle:
            self.shape.borderWidth = borderWidth
            self.shape.setStyleSheet(f'background-color: white; border-radius: {borderWidth}px;border: 3px solid white;')
        else:
            self.shape.setStyleSheet(f'background-color: black; border-radius: {borderWidth}px;border: 3px solid white;')
        self.shape.move(x,y)
        self.shape.setFixedSize(width,height)
        self.shape.show()
        return self.shape

    def generate_new_light(self,x,y,channel_number,fixture_number,light_display_window,copy):
        return RGB_light(x,y,channel_number,fixture_number,light_display_window,copy)

    def update_display(self,change_colour=False):
        self.intensity = self.channels[0][1]
        red = self.channels[1][1]
        green = self.channels[2][1]
        blue = self.channels[3][1]
        self.intensity = max(self.intensity,red,green,blue)
        if change_colour:
            self.colour = [red,green,blue]
        for i in range(5):
            self.shapes[1+i].setStyleSheet(f'background-color: rgba({red},{green},{blue},{self.intensity}); border-radius: {self.circle1.borderWidth}px;border: 3px solid rgba({red},{green},{blue},{self.intensity});')  #all borderwidths should be the same

    def update_channels_from_intensity(self):
        if max(self.colour) == 0:
            self.colour = [255]*3
        self.channels[0][1] = self.intensity
        red, green, blue = self.colour
        if red > 0:
            r = maths.floor(red/max(red,green,blue)*self.intensity)
        else:
            r=0
        if green > 0:
            g = maths.floor(green/max(red,green,blue)*self.intensity)
        else:
            g=0
        if blue > 0:
            b = maths.floor(blue/max(red,green,blue)*self.intensity)
        else:
            b=0
        self.channels[1][1] = r
        self.channels[2][1] = g
        self.channels[3][1] = b

class Miniscan(Light_type):
    def __init__(self,x,y,channel_number,fixture_number,light_display_window,copy):
        super().__init__(x,y,channel_number,fixture_number,light_display_window,copy)
        self.channels = [["Colour",0],["Gobo_roatation",0],["Gobo",0],["Intensity",0],["Pan",0],["Tilt",0],["Effects",0]]
        self.light_type = "Miniscan"
        self.clickable_region = [0,70,0,30] #in the order left right top bottom from x,y
        if self.light_display_window is not None:
            self.shapes = self.create_shapes()
            self.move()
            self.update_display()

    def create_shapes(self):
        self.box = self.create_shape(self.x,self.y,40,30,border=True)
        self.top_of_indicator = self.create_shape(self.x,self.y,25,5,border=True)
        self.bottom_of_indicator = self.create_shape(self.x,self.y,5,15,border=True)
        self.indicator = self.create_shape(self.x,self.y,10,10)
        self.select_shape = self.create_select_shape()
        return [self.box,self.top_of_indicator,self.bottom_of_indicator,self.indicator,self.select_shape]

    def create_select_shape(self):
        select_shape = QLabel(self.light_display_window)
        select_shape.move(self.x-5,self.y-5)
        select_shape.setStyleSheet("border: 1px solid orange; background-color:transparent")
        select_shape.setFixedSize(80,40)
        return select_shape

    def move(self):
        self.box.move(self.x,self.y)
        self.top_of_indicator.move(self.x+40,self.y)
        self.bottom_of_indicator.move(self.x+60,self.y+5)
        self.indicator.move(self.x+50,self.y+5)

    def create_shape(self,x,y,width,height,border = False):
        self.shape = QLabel(self.light_display_window)
        if border:
            self.shape.setStyleSheet(f'background-color: white;')
        else:
            self.shape.setStyleSheet(f'background-color: black;')
        self.shape.move(x,y)
        self.shape.setFixedSize(width,height)
        self.shape.show()
        return self.shape

    def generate_new_light(self,x,y,channel_number,fixture_number,light_display_window,copy):
        return Miniscan(x,y,channel_number,fixture_number,light_display_window,copy)

    def update_display(self,change_colour=False):
        self.intensity = self.channels[3][1]
        self.indicator.setStyleSheet(f'background-color: rgba(255,255,0,{self.intensity/255});')

    def update_channels_from_intensity(self):
        self.channels[3][1] = self.intensity

class LED_bar_24_channel(Light_type):
    def __init__(self,x,y,channel_number,fixture_number,light_display_window,copy):
        super().__init__(x,y,channel_number,fixture_number,light_display_window,copy)
        self.channels = self.setup_channels()
        self.light_type = "LED_bar_24_channel"
        self.colour = [0]*24
        self.clickable_region = [0,20,0,175] #in the order left right top bottom from x,y
        if self.light_display_window is not None:
            self.shapes = self.create_shapes()
            self.move()
            self.update_display()

    def setup_channels(self):
        channels = []
        colours = ["red","green","blue"]
        for i in range(1,9,1):
            for colour in colours:
                channels.append([colour+str(i),0])
        return channels

    def create_shapes(self):
        self.border = self.create_shape(self.x,self.y,22,162)
        for i in range(1,9,1):
            setattr(self,f"box{i}",self.create_shape(self.x,self.y,20,20))
        self.select_shape = self.create_select_shape()
        return [self.box1,self.box2,self.box3,self.box4,self.box5,self.box6,self.box7,self.box8,self.border,self.select_shape]

    def create_select_shape(self):
        select_shape = QLabel(self.light_display_window)
        select_shape.move(self.x-5,self.y-5)
        select_shape.setStyleSheet("border: 1px solid orange; background-color:transparent")
        select_shape.setFixedSize(32,172)
        return select_shape

    def move(self):
        for i in range(8):
            box = getattr(self,f"box{i+1}")
            box.move(self.x+1,self.y+20*i+1)

    def create_shape(self,x,y,width,height):
        self.shape = QLabel(self.light_display_window)
        self.shape.setStyleSheet(f'background-color: white;')
        self.shape.move(x,y)
        self.shape.setFixedSize(width,height)
        self.shape.show()
        return self.shape

    def generate_new_light(self,x,y,channel_number,fixture_number,light_display_window,copy):
        return LED_bar_24_channel(x,y,channel_number,fixture_number,light_display_window,copy)

    def update_display(self,change_colour=False):
        self.intensity = max([channel[1] for channel in self.channels])
        if change_colour:
            self.colour = [channel[1] for channel in self.channels]
        for i in range(1,9,1):
            box = getattr(self,f"box{i}")
            box.setStyleSheet(f"background-color: rgba({self.channels[(i-1)*3][1]},{self.channels[(i-1)*3+1][1]},{self.channels[(i-1)*3+2][1]},1)")

    def update_channels_from_intensity(self):
        if max(self.colour) == 0:
            self.colour = [1]*24
        for i,c in enumerate(self.colour):
            if c > 0:
                c = maths.floor(c/max(self.colour)*self.intensity)
                self.channels[i][1] = c
