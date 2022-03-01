import serial
import time


class DMX_controller(object):
    def __init__(self,port="COM3"):
        self.universe_data = [0]*513  #the first item is the start bit so should not change. Therefore there are 513 values as 0 and then 1-512
        try:
            self.ser = serial.Serial(port,baudrate=250000,bytesize=8,stopbits=2) #Creates the serial connection
            self.working = True #self.working is used for light_display to tell if dmx is being sent
        except Exception as e:
            self.working = False
            raise Exception("The serial is not working. Please make sure the lights are plugged in and that you don't have any other dmx scripts running and make sure the port is correct")


    def set_data(self,id,data):
        if isinstance(id,float): #checks if the id is a float
            raise Exception("The id needs to be an integer.")
            return
        try:
            id = int(id) #converts the id to an integer as this is required to send the dmx
        except:
            raise Exception("The id is not an integer. Please try again")
            return
        if id>512 or id<1: #checks if the id is in range
            raise Exception("The id value needs to be between 1 and 512 inclusive.")
            return
        if isinstance(data,float): #checks if the data value is a float
            raise Exception("The data value needs to be an integer")
            return
        try:
            data = int(data)
        except:
            raise Exception("The data value is not an integer. Please try again")
            return
        if data > 255 or data < 0:
            raise Exception("The data value needs to be between 0 and 255 inclusive")
            return
        # print(id)
        self.universe_data[id] = data #sets the value at address of id to data. It is not id-1 as the first bit is a start bit so remains as 0

    def send(self,universeData = None):
        if universeData is None: #checks if universe_data is passed as a paramater
            pass
        else:
            self.universe_data = universeData #allows the data to be send as a paramater into the function for example for send_full or send_zero
        self.ser.send_break(duration=92/1000000)
        time.sleep(12/1000000.0)
        try:
            self.ser.write(bytearray(self.universe_data)) #sends the data to the universe
        except:
            self.ser.close() #Closes the serial connection if it cannot write to the universe
            raise Exception("The serial cannot write. Check the cable is plugged in.")
        time.sleep(10/1000)

    def send_zero(self):
        universe_data = [0]*513 #sets all channels to off
        self.send(universe_data)

    def send_full(self):
        universe_data = [255]*512 #sets all channels to full intensity
        universe_data.insert(0,0)
        self.send(universe_data)


if __name__ == "__main__":
    dmx = DMX_controller()
    dmx.set_data(1,255)  #test data
    dmx.set_data(2,255)
    dmx.set_data(3,255)
    dmx.set_data(512,255)
    while True:
        dmx.send()
        # dmx.send_full()
        # dmx.send_zero()
