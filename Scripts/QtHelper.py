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
widget.setWindowTitle("PySide2 Example")

# show the top level widget
widget.show()

# and execute. This call will only return once `widget` is closed.
QtHelper.run(widget)
```
"""

import ix
import os


def run(widgets = None):
    """
    Start the Qt "app". This will interface a Qt event loop with Clarisse's own event loop so that both can
    coexist without blocking one another. This call will be blocking or not, depending on the `widgets` parameter.

    @note
        Do not call this with a non-None widgets paremeter form the startup script, otherwise it will block
        Clarisse's loading until the Qt window is closed.
        If you want to create a Qt application and run it through a Clarisse startup script, you need to use the
        non-blocking version of this method (e.g. call with widget as None) You can see the QtBasicStartup.py
        example script to see how it can be done.

    @param widgets
        This can be None, a single widget or a list of widgets. If not None, the call will not return unless all
        the widgets are closed. If you omit this parameter, the call returns immediately, and it's your responsability
        to make sure your UI stays alive.
    """

    # increment the running scripts count
    _increment_running_scripts()

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

    # if the script was run in blocking mode, decrement the running scripts count
    if widgets is not None:
        _decrement_running_scripts()


def app():
    """
    Return the global Qt application instance.
    """
    global _app
    return _app


def set_style(style):
    """
    Set a custom css style to the Qt application. The style supports token replacements:
    ${TOOLKIT_DIR} : path to the clarisse_toolkit repository, provided this file was not moved around and is still located in its original repository.
    ${CLARISSE_DIR} : path to Clarisse install directory.
    """
    style = style.replace("${TOOLKIT_DIR}", os.path.dirname(os.path.dirname(os.path.realpath(__file__))).replace("\\", "/"))
    style = style.replace("${CLARISSE_DIR}", ix.application.get_factory().get_vars().get("CLARISSE_BIN_DIR").get_string())
    app().setStyleSheet(style)


def set_stylesheet(filename):
    """
    Set a custom css stylesheet. This will load the content of the given file and call set_style with it.
    """
    with open(filename) as css:
        set_style(css.read())


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

def _increment_running_scripts():
    """
    Increment the number of running scripts.
    """
    if not hasattr(ix, "_running_scripts"):
        setattr(ix, "_running_scripts", 1)
        setattr(ix, "_qt_helper_event_loop", QtLoop())
    else:
        ix._running_scripts += 1

def _decrement_running_scripts():
    """
    Decrement the number of running scripts. When the count reaches 0, it will delete the Qt event loop.
    """
    if hasattr(ix, "_running_scripts"):
        ix._running_scripts -= 1
        if ix._running_scripts == 0:
            delattr(ix, "_running_scripts")
            delattr(ix, "_qt_helper_event_loop")
            print("Stopped Qt event loop.")

# get or create the global QApplication instance
_app = None
if not QApplication.instance():
    _app = QApplication([ "Clarisse" ])
else:
    _app = QApplication.instance()

# make sure it was successfully created
assert _app is not None, "Failed creating a QApplication instance."


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
        app().sendPostedEvents(None, 0)
        # add the callback to Clarisse main loop
        ix.application.add_to_event_loop_single(self.process_events)
