'''
This example is almost the same as QtBasic.py. The only difference is that it's not blocking,
meaning it can be run through a startup script.

Instructions:
- replace <path_to_repo> by the path to this repository.
- run from the command line: clarisse -startup_script "<path_to_repo>/Scripts/Examples/QtBasicStartup.py"
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

# also note: in the most cases, you'll want to start your Qt window in the startup script, but you'll
# also need to have a shelf to re-launch it in case the user closes the window. And if the user clicks
# on the shelf while the Qt window is still alive, but maybe hidden behind some other OS window, you
# want to just raise the window again.
# This is why we're using the `ix` module to store a global instance of the Qt window. This way, this
# script can be run without modification from both the startup script and a shelf. And the shelf will
# just raise the window on top, or reopen the window in case it was closed.
if not hasattr(ix, "qt_basic_startup"):
    ix.qt_basic_startup = QtWidgets.QWidget()
    textLabel = QtWidgets.QPushButton(ix.qt_basic_startup)
    textLabel.clicked.connect(test)
    textLabel.setText("Hello")
    textLabel.move(110, 85)
    ix.qt_basic_startup.setGeometry(50, 50, 320, 200)
    ix.qt_basic_startup.setWindowTitle("Qt Window")

# show it, and call raise too (in case the window is already shown, but behind another window, executing
# the script will pop the Qt window back in front)
ix.qt_basic_startup.show()
ix.qt_basic_startup.raise_()

# and run without argument: the call returns immediately and Clarisse can continue loading.
QtHelper.run()
