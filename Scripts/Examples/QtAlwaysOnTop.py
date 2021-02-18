'''
This is not really a Clarisse specific thing, but I guess it can come in handy for people wanting to integrate
their in-house pipeline tools in a Qt window that is always visible.
Basically this creates a Qt window that will always stay in front of everything.

Instructions:
- replace <path_to_repo> by the path to this repository.
'''

# import the Qt bindings first. You can import PySide, PySide2, PyQt4 or PyQt5
from PySide2 import QtCore, QtWidgets

# import our QtHelper (replace <path_to> by what's needed)
import sys
sys.path.append("<path_to_repo>/Scripts")
import QtHelper

# create a window that will stay on top of everything
widget = QtWidgets.QWidget()
# this is the flag that needs to be set. Some other flags can be used to customize the look and integration
# of the window in the OS. Check Qt's documentation https://doc.qt.io/qt-5/qwidget.html#windowFlags-prop
# and https://doc.qt.io/qt-5/qt.html#WindowType-enum
widget.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | widget.windowFlags())
widget.setGeometry(50, 50, 320, 100)
widget.setWindowTitle("Always on top Qt Window")
widget.show()

# start
QtHelper.run(widget)
