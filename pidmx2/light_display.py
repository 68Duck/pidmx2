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
from windows.slider_pannel_window import Slider_pannel_window
from windows.fixture_faders_window import Fixture_faders_window
from windows.open_rig_window import Open_rig_window
from windows.save_rig_window import Save_rig_window
from windows.select_light_type_window import Select_light_type_window
from windows.effects_window import Effects_window
from windows.open_playback_window import Open_playback_window
from windows.record_playback_window import Record_playback_window
from windows.stage_creator_window import Stage_creator_window


class Light_display(QWidget):
    def __init__(self,app):
        super().__init__()
        self.app = app
        self.database_manager = Database_manager()
        self.username = "test"  #CHANGE ME TO NONE
        self.sending_dmx = False
        self.running_raspberry_pi_dmx = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.send_dmx)
        self.raspberry_test_timer = QTimer()
        self.raspberry_test_timer.timeout.connect(self.raspberry_test)
        self.fixtures = [None]*24
        self.occupied_channels = [None]*512
        self.preview_light = None
        self.lights_to_place = []
        self.lights_info = [Generic_dimmer(None,None,None,None,None,None),RGBW_light(None,None,None,None,None,None),RGB_light(None,None,None,None,None,None),Miniscan(None,None,None,None,None,None),LED_bar_24_channel(None,None,None,None,None,None)]
        self.copy_lights = []
        self.fixture_faders_window = Fixture_faders_window(self)
        self.effects_counter = 0
        self.rig_id = None


    def update_intensities(self,intensities):
        if len(intensities) != len(self.fixtures):
            raise Exception("Intensities and fixtures should be the same length")
        for i in range(len(self.fixtures)):
            if self.fixtures[i] != None:
                self.fixtures[i].set_intensity(intensities[i])
                for l in self.copy_lights:
                    if i+1 == l.get_fixture_number():
                        l.set_intensity(intensities[i])
        try:
            self.slider_pannel_window.change_sliders_from_light()
        except Exception as e:
            # print(e)
            pass


    def update_universe_from_fixtures(self):
        for fixture in self.fixtures:
            if fixture is not None:
                channel_number = fixture.get_channel_number()
                for i,channel in enumerate(fixture.get_channels()):
                    self.set_dmx(channel_number+i,channel[1])
                    for light in self.copy_lights:
                        if light.get_channel_number() == fixture.get_channel_number() and light.get_fixture_number() == fixture.get_fixture_number():
                            light.set_channel(i,channel[1])
        self.fixture_faders_window.update_faders(self.fixtures)

    def update_universe_from_copy_light(self,light):
        for fixture in self.fixtures:
            if fixture is not None:
                if light.get_channel_number() == fixture.get_channel_number() and light.get_fixture_number() == fixture.get_fixture_number():
                    channel_number = light.get_channel_number()
                    for i,channel in enumerate(light.get_channels()):
                        self.set_dmx(channel_number+i,channel[1])
                        fixture.set_channel(i,channel[1])

        for l in self.copy_lights:
            if light.get_channel_number() == l.get_channel_number() and light.get_fixture_number() == l.get_fixture_number():
                channel_number = light.get_channel_number()
                for i,channel in enumerate(light.get_channels()):
                    self.set_dmx(channel_number+i,channel[1])
                    l.set_channel(i,channel[1])
        self.fixture_faders_window.update_faders(self.fixtures)

    def add_fixture(self,x,y,light_type,fixture_number,channel_number,light_display_window,copy=False,channels=None):
        if self.preview_light:
            self.preview_light.hide()
        if self.fixtures[fixture_number-1] is not None:
            return "Fixture is already taken"
        else:
            self.new_light = None
            for light in self.lights_info:
                if light.get_light_type() == light_type:
                    channels_valid = self.check_channels(start_channel = channel_number,no_channels=len(light.get_channels()))
                    if channels_valid:
                        self.new_light = light.generate_new_light(x,y,channel_number,fixture_number,light_display_window,copy=False)
                        if channels is not None:
                            self.new_light.set_channels(channels)
                        self.fixtures[fixture_number-1] = self.new_light #-1 since fixture number is 1 indexed not 0
                        for i in range(len(light.channels)):
                            self.occupied_channels[channel_number+i-1] = self.new_light  #-1 since fixture number is 1 indexed not 0
                        self.fixture_faders_window.update_faders(self.fixtures)
                        return True
                    elif copy:
                        self.new_copy_light = light.generate_new_light(x,y,channel_number,fixture_number,light_display_window,copy=True)
                        self.copy_lights.append(self.new_copy_light)
                        for fixture in self.fixtures:
                            if fixture is not None:
                                if self.new_copy_light.get_channel_number() == fixture.get_channel_number() and self.new_copy_light.get_fixture_number() == fixture.get_fixture_number():
                                    channel_number = fixture.get_channel_number()
                                    for i,channel in enumerate(fixture.get_channels()):
                                        self.new_copy_light.set_channel(i,channel[1])
                                    if fixture.is_selected():
                                        self.new_copy_light.toggle_selected()
                        self.fixture_faders_window.update_faders(self.fixtures)
                        return True
                    else:
                        return "There are overlapping channels"
        return f"No light with {light_type} type exists"

    def check_new_fixture(self,light_type,fixture_number,channel_number):
        if fixture_number > len(self.fixtures) or fixture_number < 1:
            return "The fixture number is not in the correct range"
        if self.fixtures[fixture_number-1] is not None: #-1 since fixture number is 1 indexed not 0
            return "There is already a fixture with that number. Please try again"
        else:
            self.new_light = None
            for light in self.lights_info:
                if light.get_light_type() == light_type:
                    channels_valid = self.check_channels(start_channel = channel_number,no_channels=len(light.get_channels()))
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
        return [light.get_light_type() for light in self.lights_info]


    def place_fixture(self,light_type,fixture_number,channel_number,copy=False,channels=None):
        self.light_display_window.place_fixture(light_type,fixture_number,channel_number,copy,channels)

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

    def check_for_light_click(self,x,y):
        for light in self.fixtures:
            if light is not None:
                if light.check_for_click(x,y):
                    self.run_slider_pannel_window(light)
        for light in self.copy_lights:
            if light.check_for_click(x,y):
                self.run_slider_pannel_window(light)

    def check_for_light_select(self,x,y):
        for fixture in self.fixtures:
            if fixture is not None:
                if fixture.check_for_click(x,y):
                    fixture.toggle_selected()
                for light in self.copy_lights:
                    if fixture.get_fixture_number() == light.get_fixture_number():
                        light.toggle_selected()

        for light in self.copy_lights:
            if light.check_for_click(x,y):
                light.toggle_selected()
                for fixture in self.fixtures:
                    if fixture is not None:
                        if fixture.get_fixture_number() == light.get_fixture_number():
                            fixture.toggle_selected()
                for l in self.copy_lights:
                    if l.get_fixture_number() == light.get_fixture_number():
                        l.toggle_selected()

    def delete_fixture(self,light):
        #search if any copy lights first
        fixture_number = light.get_fixture_number()
        channel_number = light.get_channel_number()
        channels = light.get_channels()
        if light.is_copy() and light not in self.fixtures:
            self.copy_lights.remove(light)
        else:
            for l in self.copy_lights:
                if l.get_fixture_number() == fixture_number:
                    self.fixtures[fixture_number-1] = l
                    self.copy_lights.remove(l)
                    return
            #if reaches here then there are no copy lights so the light should be deleted completely
            self.fixtures[fixture_number-1] = None
            for i in range(len(channels)):
                self.occupied_channels[channel_number+i-1] = None
            self.fixture_faders_window.update_faders(self.fixtures)



    def preview_fixture(self,x,y,light_type,light_display_window):
        if self.preview_light:
            self.preview_light.hide()
        for light in self.lights_info:
            if light.get_light_type() == light_type:
                self.preview_light = light.generate_new_light(x,y,None,None,light_display_window,False)

    def get_no_channels(self,light_type):
        for light in self.lights_info:
            if light.get_light_type() == light_type:
                return len(light.get_channels())
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

    def run_slider_pannel_window(self,light):
        self.slider_pannel_window = Slider_pannel_window(light,self)
        self.slider_pannel_window.show()

    def wired_DMX(self,port):
        self.dmx_controller = DMX_controller(port)
        self.sending_dmx = True
        self.timer.start(0)
        self.run_light_display_window()

    def send_dmx(self):
        self.tick_effects()
        if self.sending_dmx:
            self.dmx_controller.send()
        if self.running_raspberry_pi_dmx:
            pass  #finish me

    def tick_effects(self):
        self.effects_counter += 1
        for fixture in self.fixtures:
            if fixture is not None:
                fixture.run_effects(self.effects_counter)


    def set_dmx(self,channel_number,channel_value):
        if self.sending_dmx:
            self.dmx_controller.set_data(channel_number,channel_value)

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

    def run_fixture_faders_window(self):
        self.fixture_faders_window.show()
        self.fixture_faders_window.update_faders(self.fixtures)
        monitor = QDesktopWidget().screenGeometry(1)
        self.fixture_faders_window.move(monitor.left(), monitor.top())
        self.fixture_faders_window.showMaximized()

    def run_open_rig_window(self):
        self.open_rig_window = Open_rig_window(self,self.database_manager)
        self.open_rig_window.show()

    def run_save_rig_window(self):
        self.save_rig_window = Save_rig_window(self,self.database_manager)
        self.save_rig_window.show()

    def run_select_light_type_window(self):
        self.select_light_type_window = Select_light_type_window(self)
        self.select_light_type_window.show()

    def run_effects_window(self):
        self.effects_window = Effects_window(self)
        self.effects_window.show()

    def run_open_playback_window(self):
        self.open_playback_window = Open_playback_window(self,self.database_manager)
        # self.open_playback_window.show() #not called since called within init which is required for error open window sequencing

    def run_record_playback_window(self):
        self.record_playback_window = Record_playback_window(self,self.database_manager)
        # self.record_playback_window.show()  #not called since called within init which is required for error open window sequencing

    def run_stage_creator_window(self):
        self.stage_creator_window = Stage_creator_window(self,self.database_manager)
        self.app.installEventFilter(self.stage_creator_window)
        self.stage_creator_window.show()

    def select_light_type(self,light_type):
        for fixture in self.fixtures:
            if fixture is not None:
                if fixture.get_light_type() == light_type and not fixture.is_selected():
                    fixture.toggle_selected()

    def update_fixture_faders_selected_buttons(self):
        self.fixture_faders_window.update_select_buttons(self.fixtures)

    def toggle_fixture(self,fixture_number):
        if self.fixtures[fixture_number-1] is not None:
            self.fixtures[fixture_number-1].toggle_selected(update_faders=False)

    def raspberry_pi_login(self,password):
        self.raspberry_pi_password = password
        self.running_raspberry_pi_dmx = True
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
        self.timer.start(0)
        self.run_light_display_window()

    def test_port(self,port):
        try:
            dmx = DMX_controller(port)
            return dmx.working
        except:
            return False

    def get_account_id(self):
        try:
            account_id = self.database_manager.query_db("SELECT account_id FROM Accounts WHERE username=?",(self.username,))[0]["account_id"]
            return account_id
        except:
            return False

    def get_rig_id(self):
        return self.rig_id


    def logged_in(self,username):
        self.username = username
        self.logon_window.close()
        self.run_mode_selection_window()

    def get_fixtures(self):
        return self.fixtures

    def get_copy_lights(self):
        return self.copy_lights

    def open_rig(self,fixtures,rig_id):
        self.rig_id = rig_id
        for f in self.fixtures:
            if f is not None:
                f.hide()
        for c in self.copy_lights:
            c.hide()
        self.fixtures = [None]*24
        self.occupied_channels = [None]*512
        self.copy_lights = []
        for fixture in fixtures:
            copy = False
            for f in self.fixtures:
                if f is not None:
                    if f.get_fixture_number() == fixture["fixture_number"]:
                        copy = True
            self.add_fixture(fixture["xpos"],fixture["ypos"],fixture["light_type"],fixture["fixture_number"],fixture["start_channel"],self.light_display_window,copy)
        self.fixture_faders_window.update_faders(self.fixtures)

    def open_playback(self,channel_values,light_effects):
        for fixture in self.fixtures: #Clear effects
            if fixture is not None:
                fixture.set_effects({"Rainbow":0,"Chaser":0})

        for channel in channel_values:
            for fixture in self.fixtures:
                if fixture is not None:
                    if fixture.get_channel_number() <= channel["channel_number"] and fixture.get_channel_number() + len(fixture.get_channels()) > channel["channel_number"]:
                        channel_index = channel["channel_number"] - fixture.get_channel_number()  #should work since both one indexed
                        fixture.set_channel(channel_index,channel["channel_value"],change_colour = True)
        for effect in light_effects:
            for fixture in self.fixtures:
                if fixture is not None:
                    light_id = self.database_manager.query_db("SELECT light_id FROM Lights WHERE light_type = ? AND start_channel = ? AND xpos = ? and ypos = ?",(fixture.get_light_type(),fixture.get_channel_number(),fixture.get_x(),fixture.get_y()))
                    light_id = light_id[0]["light_id"]
                    if light_id == effect["light_id"]:
                        fixture.set_effect(effect["effect_name"],effect["effect_value"])

        self.fixture_faders_window.update_faders(self.fixtures)
        self.update_universe_from_fixtures()
