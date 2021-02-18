'''
This example script is the most basic Qt integration script. It uses our QtHelper script and
creates a small window with a push button. The script does not return until the window is
closed.

Instructions:
- replace <path_to_repo> by the path to this repository.
'''

# import the Qt bindings first. You can import PySide, PySide2, PyQt4 or PyQt5
from PySide2 import QtCore, QtWidgets

# import our QtHelper (replace <path_to> by what's needed)
import sys
sys.path.append("<path_to_repo>/Scripts")
import QtHelper

# example callback for a push button
def test():
    ix.log_info("Hello from Qt")

# create a small window with a push button
widget = QtWidgets.QWidget()
textLabel = QtWidgets.QPushButton(widget)
textLabel.clicked.connect(test)
textLabel.setText("Hello")
textLabel.move(110, 85)
widget.setGeometry(50, 50, 320, 200)
widget.setWindowTitle("Qt Window")

# show it
widget.show()

# and run. This will not return until the widget is closed
QtHelper.run(widget)
