'''
This example is almost the same as QtBasic.py. The only difference is that it's not blocking,
meaning it can be run through a startup script.
Usage: clarisse -startup_script "<path_to>/QtBasicStartup.py"
'''

# import the Qt bindings first. You can import PySide, PySide2, PyQt4 or PyQt5
from PySide2 import QtCore, QtWidgets

# import our QtHelper (replace <path_to> by what's needed)
import sys
sys.path.append("<path_to>/clarisse_toolkit/Scripts")
import QtHelper

# example callback for a push button
def test():
    ix.log_info("Hello from Qt")

# create a small window with a push button
# note that this time we create the widget directly in the `ix` module, to make sure it stays alive
# also note: we test if the widget already exists, because in most cases, you will want to start the app
# on startup, and also have a shelf button to re-launch the app, in case the user closes it.
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
