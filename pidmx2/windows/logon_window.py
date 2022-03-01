from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys
import hashlib

 #imports the necessary imports from the other files
from windows.error_window import Error_window

class Logon_window(QWidget,uic.loadUiType(os.path.join("windows/ui","logon_window.ui"))[0]):
    def __init__(self,light_display,database_manager):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Logon window") #sets the title of the window
        self.database_manager = database_manager
        self.light_display = light_display
        self.initUI()

    def initUI(self): #sets up the user interface
        self.username_input.setFocus() #sets the cursor to start on the username input
        self.submit_button.clicked.connect(self.submit_pressed) #calls the submit_pressed function when the submit button is pressed
        self.username_input.setPlaceholderText("Enter Username") #sets the placeholder text of the inputs
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.Password) #sets the text input to dots so the password is hidden
        self.create_account_button.clicked.connect(self.create_account_pressed)

    def create_account_pressed(self):
        self.light_display.run_create_account_window()
        self.close()

    def keyPressEvent(self,e): #on the enter key being pressed, call the submit_pressed function
        if e.key() == Qt.Key_Return:
            self.submit_pressed()

    def submit_pressed(self): #when the submit button is pressed
        username = self.username_input.text() #retrive the username and passwords input
        password = self.password_input.text()

        m = hashlib.sha256() #hashes the password using the sha256 algorithmn
        m.update(password.encode("utf8"))
        hashed_password = m.digest()

        results = self.database_manager.query_db("SELECT * FROM Accounts WHERE username = ? AND hashed_password = ?",(username,hashed_password)) #retrieves all records with the same username. There should only be one if any exist since usernames are unique
        if len(results)>0:
            message_window = QtWidgets.QMessageBox.question(self,"Message","Logged in as "+username,QtWidgets.QMessageBox.Ok) #displays the message
            self.light_display.logged_in(username)
        else:
            self.username_input.setText("") #remvoves the input username and password
            self.password_input.setText("")
            self.error_window = Error_window("The username or password is not valid. Please try again.") #displays an error message stating the login deatils are invalid
