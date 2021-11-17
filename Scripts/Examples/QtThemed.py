'''
This example script is the most basic Qt integration script. It uses our QtHelper script and
creates a small window with a push button. The script does not return until the window is
closed.

Instructions:
- replace <path_to_repo> by the path to this repository.
'''

# import the Qt bindings first. You can import PySide, PySide2, PyQt4 or PyQt5
from PySide2 import QtWidgets

# the path to the clarisse_toolkit repository (replace by the real one)
repository = "..."

# import our QtHelper
import sys
sys.path.append(repository)
import QtHelper

# create a small window with a push button
widget = QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout()
layout.addWidget(QtWidgets.QPushButton("Push Me"))
layout.addWidget(QtWidgets.QCheckBox("Check Me"))
layout.addWidget(QtWidgets.QLineEdit("Edit Me"))
layout.addWidget(QtWidgets.QSpinBox())
combo = QtWidgets.QComboBox()
combo.insertItems(0, [ "Choose", "Me" ])
layout.addWidget(combo)
layout.addStretch()
widget.setGeometry(50, 50, 240, 200)
widget.setWindowTitle("Themed")
widget.setLayout(layout)

# set the style
QtHelper.set_stylesheet("{}/../Themes/Qt.css".format(repository))

# show it
widget.show()

# and run. This will not return until the widget is closed
QtHelper.run(widget)
