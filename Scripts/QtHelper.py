"""
This module helps integrating Qt stuff in Clarisse.
It must be imported AFTER having imported your Qt binding module (PySide(2), PyQt, etc.)
Here is a very basic example:

```
# import Qt bindings
from PySide2 import QtCore, QtWidgets
# import this helper
import QtHelper

# from here, you can create your UI like usual
widget = QtWidgets.QWidget()

textLabel = QtWidgets.QLabel(widget)
textLabel.setText("Hello")
textLabel.move(110, 85)

widget.setGeometry(50, 50, 320, 200)
widget.setWindowTitle("PyQt5 Example A")

# show the top level widget
widget.show()

# and execute. This call will only return once `widget` is closed.
app.run(widget)
```
"""
import ix


def run(widgets = None):
    """
    Start the Qt "app". This will interface a Qt event loop with Clarisse's own event loop so that both can
    coexist without blocking one another. This call be be blocking or not, depending on the `widgets` paramter.

    @param widgets
        This can be None, a single widget or a list of widgets. If not None, the call will not return unless all
        the widgets are closed. If you omit this parameter, the call returns immediately, and it's your responsability
        to make sure your UI stays alive.
    """

    # install our event loop in Clarisse, if it's not already
    if not hasattr(ix, "_qt_helper_event_loop"):
        ix._qt_helper_event_loop = QtLoop()

    # if widgets is None, return immediately
    if widgets is None:
        return

    # make sure widgets is a list
    if not isinstance(widgets, list):
        widgets = [ widgets ]

    # wait until all widgets are closed
    while any(w.isVisible() for w in widgets):
        # process Clarisse loop
        ix.application.check_for_events()


#######################################################################################################################
#
# The following is meant to be "private", e.g. it's not meant to be used by scripts that import this file as a module.
#
#######################################################################################################################


import sys


def _get_qt():
    """
    This function will check loaded modules to try and guess which version was loaded. In case no version or
    multiple ones were loaded, it will log an error and return nothing.

    @note
        This function is "private" and shouldn't be used directly by anthing other than this module.

    @returns
        The QApplication and QEventLoop classes as a pair
    """
    # check which versions of Qt are loaded
    pyqt4 = 1 if "PyQt4" in sys.modules else 0
    pyqt5 = 1 if "PyQt5" in sys.modules else 0
    pyside = 1 if "PySide" in sys.modules else 0
    pyside2 = 1 if "PySide2" in sys.modules else 0

    # get the number of loaded versions
    loaded_qt_versions = pyqt4 + pyqt5 + pyside + pyside2

    # if no version of Qt is loaded, or if multiple ones are, throw an exception
    if loaded_qt_versions == 0:
        raise Exception("QtHelper - no known Qt module found. Try importing PyQt4/5 or PySide/2 **before** importing QtHelper")
    elif loaded_qt_versions > 1:
        raise Exception("QtHelper - more than one Qt module loaded! Load **only** one of PyQt4/5 or PySide/2 before importing QtHelper")

    # here we can actually load the correct version of Qt and return its QtCore and QtGui parts.
    if pyqt4 == 1:
        ix.log_info("Python: using PyQt4 Qt bindings.")
        from PyQt4 import QtCore, QtGui
        return QtGui.QApplication, QtCore.QEventLoop
    elif pyqt5 == 1:
        ix.log_info("Python: using PyQt5 Qt bindings.")
        from PyQt5 import QtCore, QtWidgets
        return QtWidgets.QApplication, QtCore.QEventLoop
    elif pyside == 1:
        ix.log_info("Python: using PySide Qt bindings.")
        from PySide import QtCore, QtGui
        return QtGui.QApplication, QtCore.QEventLoop
    elif pyside2 == 1:
        ix.log_info("Python: using PySide2 Qt bindings.")
        from PySide2 import QtCore, QtWidgets
        return QtWidgets.QApplication, QtCore.QEventLoop


# load QApplication and QEventLoop
QApplication, QEventLoop = _get_qt()


# get or create the global QApplication instance
qt_app = None
if not QApplication.instance():
    qt_app = QApplication([ "Clarisse" ])
else:
    qt_app = QApplication.instance()

# make sure it was successfully created
assert qt_app is not None, "Failed creating a QApplication instance."


class QtLoop:
    """
    This class is used to interface Qt and Clarisse event loops. What it does is that it installs a callback in the
    Clarisse's main loop. When this callback is executed, it will process the Qt events, and install itself again.

    @note
        This class should not be used outside of this module. It's only meant to be instanciated once.
    """

    def __init__(self):
        """
        Initialization method. This will store the app and install this instance in the Clarisse's event loop.
        """
        # create a dedicated loop
        self.event_loop = QEventLoop()
        # install an event callback that will be processed on the main loop
        ix.application.add_to_event_loop_single(self.process_events)

    def process_events(self):
        """
        This is called from CLarisse's main loop. It will then process Qt events, and install this callback in Clarisse
        event loop again.
        """
        # process Qt's events
        self.event_loop.processEvents()
        # flush Qt's stacked events
        qt_app.sendPostedEvents(None, 0)
        # add the callback to Clarisse main loop
        ix.application.add_to_event_loop_single(self.process_events)
