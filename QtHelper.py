"""
This module helps integrating Qt stuff in Clarisse.
It must be imported AFTER having imported your Qt binding module (PySide(2), PyQt, etc.)
Here is a very basic example:

```
# import Qt bindings
from PySide2 import QtCore, QtWidgets
# import this helper
import QtHelper

# create the Qt app
app = QtHelper.App()

# from here, you can create your UI like usual
widget = QtWidgets.QWidget()

textLabel = QtWidgets.QLabel(widget)
textLabel.setText("Hello")
textLabel.move(110, 85)

widget.setGeometry(50, 50, 320, 200)
widget.setWindowTitle("PyQt5 Example A")

# show the top level widget
widget.show()

# and execute. This call will only return once the top level widget is closed.
app.exec_(widget)
```
"""
import ix
import sys


class App:
    """
    This class encapsulate a QApplication and should be used instead of QApplication.
    It will allow creating Qt application without freezing Clarisse's UI.
    Note that this class should not be used if some other scripts are using the old
    way (e.g. pyqt_clarisse.exec_() global function)

    Using this class (see the example use in the module's documentation) is highly
    recommended as it will correctly handle concurrently running multiple scripts
    with Qt stuff.
    """

    ## The Qt application. There is only 1 instance of this, always
    qt_app = None

    ## Global event loop that we're using to interface with Clarisse's
    event_loop = None

    @staticmethod
    def _are_windows_visible(widgets = None):
        """
        This static method will check if there are still some visible widgets. If no argument
        is passed, it'll check all the top level widgets (See QApplication.topLevelWidgets)
        otherwise the passed argument should be a list of widgets to check.
        Returns True if at list one widget is still visible.
        """
        if widgets is None:
            widgets = _qt_gui.QApplication.topLevelWidgets()
        return any(w.isVisible() for w in widgets)

    @staticmethod
    def _process_events(unused=None):
        """
        This is a callback that will be called from the main Clarisse event loop. It's used
        to correctly mix both Qt and Clarisse event loops.
        """
        if App._are_windows_visible() is True:
            # call Qt main loop
            App.event_loop.processEvents()
            # flush stacked events
            App.qt_app.sendPostedEvents(None, 0)
            # add ourself again to Clarisse's main event loop
            ix.application.add_to_event_loop_single(App._process_events)
        else:
            # quit and destroy the global app
            ix.log_info("Stoppig global Qt app")
            App.qt_app.quit()
            App.qt_app = None

    def __init__(self):
        """
        Initialization method.
        """
        if App.qt_app is None:
            # create (or get) the QApplication
            if _qt_gui.QApplication.instance() is None:
                App.qt_app = _qt_gui.QApplication([ "Clarisse" ])
            else:
                App.qt_app = _qt_gui.QApplication.instance()

            # create the event loop
            App.event_loop = _qt_core.QEventLoop()

            # start the event loop
            ix.application.add_to_event_loop_single(App._process_events)

        # the top level widgets handled by this app
        top_level_widgets = []

    def exec_(self, widgets):
        """
        exec_ overload. Once the application has been created, and all the UI created,
        call this method. The argument passed can be either None, a signel widget or
        a list of widgets.
        When None is passed, the exec_ method will not return until there is no longer
        any visible top level Qt widget. If you do that, your script will not return
        if another script is running with a Qt widget.
        When either a single widget or of list of them is passed, the exec_ method will
        not return until said widget(s) is(are) no longer visible.
        """
        if widgets is not None:
            if isinstance(widgets, list):
                self.top_level_widgets = widgets
            else:
                self.top_level_widgets = [ widgets ]
        else:
            self.top_level_widgets = None

        # start processing events
        while App._are_windows_visible(self.top_level_widgets) is True:
            ix.application.check_for_events()


def _get_qt():
    """
    This function will check loaded modules to try and guess which version was
    loaded. In case no version or multiple ones were loaded, it will log an error
    and return nothing.

    @note
        This function is "private" and shouldn't be used directly by anthing
        other than this module.

    @returns
        A pair containing the QtCore and QtGui/QtWidgets modules in that order.
        Both modules can be None in case of errors. Note that the second module
        is the one containing QApplication. Depending on the Qt version and binding
        used, QApplication can be in QtGui or QtWidget.
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
        return QtCore, QtGui
    elif pyqt5 == 1:
        ix.log_info("Python: using PyQt5 Qt bindings.")
        from PyQt5 import QtCore, QtWidgets
        return QtCore, QtWidgets
    elif pyside == 1:
        ix.log_info("Python: using PySide Qt bindings.")
        from PySide import QtCore, QtGui
        return QtCore, QtGui
    elif pyside2 == 1:
        ix.log_info("Python: using PySide2 Qt bindings.")
        from PySide2 import QtCore, QtWidgets
        return QtCore, QtWidgets


# load QtCore and QtGui (or QtWidgets in case Qt5 is used)
_qt_core, _qt_gui = _get_qt()
