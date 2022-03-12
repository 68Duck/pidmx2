from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
import sys

from light_display import Light_display

sys._excepthook = sys.excepthook


def my_exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)

sys.excepthook = my_exception_hook


if __name__ == "__main__":
    app = QApplication(sys.argv)
    light_display = Light_display(app) #Creates an instance of the light display class
    # light_display.run_logon_window() #Runs the logon window so it displays on the screen
    light_display.run_light_display_window() #Runs the logon window so it displays on the screen
    # light_display.run_mode_selection_window() #Runs the logon window so it displays on the screen
    # light_display.run_sequence_window() #Runs the logon window so it displays on the screen
    sys.exit(app.exec_())
