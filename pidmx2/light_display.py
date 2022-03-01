from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import sys

from database_manager import Database_manager
from dmx_controller import DMX_controller
from raspberry_pi_manager import Raspberry_pi_manager
from light_types import Generic_dimmer,RGBW_light,RGB_light,Miniscan,LED_bar_24_channel
sys.path.insert(1,"/windows")
from windows.logon_window import Logon_window
from windows.mode_selection_window import Mode_selection_window
from windows.create_account_window import Create_account_window
from windows.light_display_window import Light_display_window
from windows.port_selection_window import Port_selection_window
from windows.ip_address_selection_window import Ip_address_selection_window
from windows.raspberry_pi_password_input_window import Raspberry_pi_password_input_window
from windows.error_window import Error_window
from windows.patching_window import Patching_window


class Light_display(QWidget):
    def __init__(self,app):
        super().__init__()
        self.app = app
        self.database_manager = Database_manager()
        self.username = "test"  #CHANGE ME TO NONE
        self.sending_dmx = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.send_dmx)
        self.raspberry_test_timer = QTimer()
        self.raspberry_test_timer.timeout.connect(self.raspberry_test)
        self.fixtures = [None]*24
        self.occupied_channels = [None]*512
        self.preview_light = None
        self.lights_to_place = []
        self.lights_info = [Generic_dimmer(None,None,None,None,None),RGBW_light(None,None,None,None,None),RGB_light(None,None,None,None,None),Miniscan(None,None,None,None,None),LED_bar_24_channel(None,None,None,None,None)]

    def add_fixture(self,x,y,light_type,fixture_number,channel_number,light_display_window):
        if self.fixtures[fixture_number] is not None:
            return "Fixture is already taken"
        else:
            self.new_light = None
            for light in self.lights_info:
                if light.light_type == light_type:
                    channels_valid = self.check_channels(start_channel = channel_number,no_channels=len(light.channels))
                    if channels_valid:
                        self.new_light = light.generate_new_light(x,y,channel_number,fixture_number,light_display_window)
                        self.fixtures[fixture_number-1] = self.new_light #-1 since fixture number is 1 indexed not 0
                        for i in range(len(light.channels)):
                            self.occupied_channels[channel_number+i-1] = self.new_light  #-1 since fixture number is 1 indexed not 0
                        return True
                    else:
                        return "There are overlapping channels"
        return f"No light with {light_type} type exists"

    def check_new_fixture(self,light_type,fixture_number,channel_number):
        if self.fixtures[fixture_number-1] is not None: #-1 since fixture number is 1 indexed not 0
            return "There is already a fixture with that number. Please try again"
        else:
            self.new_light = None
            for light in self.lights_info:
                if light.light_type == light_type:
                    channels_valid = self.check_channels(start_channel = channel_number,no_channels=len(light.channels))
                    if channels_valid:
                        return True
                    else:
                        return "There are overlapping channels or the channels are out of range. Please try again"
        return f"No light with {light_type} type exists"

    def check_if_channel_free(self,channel_number):
        return self.occupied_channels[channel_number-1] is None #-1 since occupied_channels is 0 indexed

    def check_if_fixture_free(self,fixture_number):
        return self.fixtures[fixture_number-1] is None #-1 since occupied_channels is 0 indexed

    def get_light_types(self):
        return [light.light_type for light in self.lights_info]


    def place_fixture(self,light_type,fixture_number,channel_number):
        self.light_display_window.place_fixture(light_type,fixture_number,channel_number)

    def setup_next_light_to_place(self):
        valid = len(self.lights_to_place)>0
        if valid:
            next_light = self.lights_to_place.pop(0)
            self.place_fixture(next_light["light_type"],next_light["fixture_number"],next_light["channel_number"])
        return valid

    def place_multiple_lights(self,lights_to_place_array):
        for record in lights_to_place_array:
            self.lights_to_place.append(record)
        self.setup_next_light_to_place()

    def preview_fixture(self,x,y,light_type,light_display_window):
        if self.preview_light:
            self.preview_light.hide()
        for light in self.lights_info:
            if light.light_type == light_type:
                self.preview_light = light.generate_new_light(x,y,None,None,light_display_window)

    def get_no_channels(self,light_type):
        for light in self.lights_info:
            if light.light_type == light_type:
                return len(light.channels)
        return False

    def check_channels(self,start_channel,no_channels):
        if start_channel+no_channels-1>512: #-1 since the channel is valid if it is 512
            return False
        for i in range(no_channels):
            if self.occupied_channels[start_channel+i-1] is not None: #-1 since occupied_channels is 0 indexed
                return False
        return True

    def run_logon_window(self):
        self.logon_window = Logon_window(self,self.database_manager)
        self.logon_window.show()

    def run_create_account_window(self):
        self.create_account_window = Create_account_window(self,self.database_manager)
        self.create_account_window.show()

    def run_mode_selection_window(self):
        self.mode_selection_window = Mode_selection_window(self)
        self.mode_selection_window.show()
        self.timer.stop()
        self.raspberry_test_timer.stop()
        self.sending_dmx = False
        try:
            self.raspberry_pi_manager.send_stop()
            del self.raspberry_pi_manager
        except Exception as e:
            print(e)
        try: #close any dmx controllers if they exist
            self.dmx_controller.ser.close()
            del self.dmx_controller
        except:
            pass

    def run_light_display_window(self):
        if self.username is not None:
            self.light_display_window = Light_display_window(self,self.username,self.database_manager)
            self.app.installEventFilter(self.light_display_window)
            self.light_display_window.show()
        else:
            raise Exception("Username is not defined")

    def wired_DMX(self,port):
        self.dmx_controller = DMX_controller(port)
        self.sending_dmx = True
        self.timer.start(0)
        self.run_light_display_window()

    def send_dmx(self):
        if self.sending_dmx:
            self.dmx_controller.send()

    def raspberry_test(self):
        result = self.raspberry_pi_manager.send_command("test")
        if result == "ERROR":
            try:
                self.dmx_controller.ser.close()
                del self.raspberry_pi_manager
            except:
                pass
            self.error_window = Error_window("Raspberry pi error. Please check the cable is still plugged in.")
            self.raspberry_test_timer.stop()

    def raspberry_pi_DMX(self,ipv4):
        self.ipv4 = ipv4
        self.run_raspberry_pi_password_input_window()


    def run_ip_address_selection_window(self):
        self.ip_address_selection_window = Ip_address_selection_window(self,self.database_manager)
        self.ip_address_selection_window.show()

    def run_port_selection_window(self):
        self.port_selection_window = Port_selection_window(self)
        self.port_selection_window.show()

    def run_raspberry_pi_password_input_window(self):
        self.raspberry_pi_password_input_window = Raspberry_pi_password_input_window(self)
        self.raspberry_pi_password_input_window.show()

    def run_patching_window(self):
        self.patching_window = Patching_window(self)
        self.patching_window.show()

    def raspberry_pi_login(self,password):
        self.raspberry_pi_password = password
        self.raspberry_pi_manager = Raspberry_pi_manager(self.ipv4,self.raspberry_pi_password)
        try:
            self.raspberry_pi_manager.run_file()
            self.raspberry_pi_manager.connect_client()
            self.raspberry_test_timer.start(1000)
            self.run_light_display_window()
            return True
        except Exception as e:
            print(e)
            self.raspberry_pi_manager.run_file_client.close()
            del self.raspberry_pi_manager
            return e


    def no_DMX(self):
        self.run_light_display_window()

    def test_port(self,port):
        try:
            dmx = DMX_controller(port)
            return dmx.working
        except:
            return False


    def logged_in(self,username):
        self.username = username
        self.logon_window.close()
        self.run_mode_selection_window()
