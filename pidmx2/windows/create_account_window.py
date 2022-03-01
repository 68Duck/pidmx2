from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import*
from PyQt5.QtGui import*
from PyQt5.QtCore import*
import os
import sys
import hashlib

from windows.error_window import Error_window
from windows.message_window import Message_window

class Create_account_window(QWidget,uic.loadUiType(os.path.join("windows/ui","create_account_window.ui"))[0]):
    def __init__(self,light_display,database_manager):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Create Account Window")
        self.database_manager = database_manager
        self.light_display = light_display
        self.initUI()

    def initUI(self): #sets up the user interface
        self.username_input.setFocus() #sets the cursor to start on the username input
        self.submit_button.clicked.connect(self.submit_pressed) #calls the submit_pressed function when the submit button is pressed
        self.back_button.clicked.connect(self.back_pressed)
        self.username_input.setPlaceholderText("Enter Username") #sets the placeholder text of the inputs
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.Password) #sets the text input to dots so the password is hidden

    def keyPressEvent(self,e): #on the enter key being pressed, call the submit_pressed function
        if e.key() == Qt.Key_Return:
            self.submit_pressed()

    def back_pressed(self):
        self.light_display.run_logon_window()
        self.close()

    def check_valid_characters(self,string): #checks if the characters input are able to use the utf-8 encoding
        try:
            string.encode("utf-8")
            return True
        except UnicodeError:
            return False

    def submit_pressed(self): #when the submit button is pressed
        username = self.username_input.text()#retrive the username and passwords input
        password = self.password_input.text()

        usernames = self.database_manager.query_db("SELECT username FROM Accounts WHERE username = ?",(username,)) #retrive any records where the username is the same as the username input

        self.username_input.setText("") #removes the input username and password
        self.password_input.setText("")

        if len(usernames) > 0: #if there are usernames with the same name show an error message
            self.error_window = Error_window("There is already an account with the same username. Please try again")
            return
        elif len(username) > 16 or len(username) < 3: #if the username is of an invalid length show na error message
            self.error_window = Error_window("The username must be between 3 and 16 characters in length. Please try a different username")
            return
        elif self.check_valid_characters(username) is False: #if any invalid characters are invalid show an error message
            self.error_window = Error_window("The username contains invalid characters. Please try again.")
            return
        elif len(password) == 0: #if no password is input show an error message
            self.error_window = Error_window("Please input a password")
            return

        m = hashlib.sha256() #hash the password using the sha256 algorithmn
        m.update(password.encode("utf8"))
        hashed_password = m.digest()

        self.database_manager.query_db("INSERT INTO Accounts(username,hashed_password) VALUES(?,?)",(username,hashed_password)) #insert the username and hashed_password into the Accounts table
        message_window = QtWidgets.QMessageBox.question(self,"Message",f"An account with name {username} has been created.",QtWidgets.QMessageBox.Ok) #displays the message



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Create_account_window(Database_manager())
    win.show()
    sys.exit(app.exec_())
