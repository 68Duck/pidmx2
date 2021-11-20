# PiDMX2
Python DMX controller interface with Pyqt5 and raspberry pi


# Installation
To install the project first create a new directory. Then in the command line type cd and then paste in the address of the new directory.

Then type in the command line:
`git clone https://github.com/68Duck/pidmx2`

and then:
`pip install -r pidmx2/requirements.txt`

to install all of the required imports.

# Features

Allows the controlling of lights using DMX (digital multiplex) with a USB to DMX cable. This can be plugged directly into a computer or plugged into a raspberry pi and run through there via SSH.

You can create your own lighting rig by moving around fixtures on the screen by patching them using the patch button. Then just click on the light to control the light.

Different users can use the project with the included login system. Just create an account to start using the system.


#Naming Conventions Used

Variables using lowercase and using underscores to separate words (snakecase) e.g. my_variable

Constants using all uppercase e.g. CONSTANT

Classes using upper case camel case e.g. MyClass
