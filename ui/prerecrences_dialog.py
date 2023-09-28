from PyQt5 import QtWidgets, uic, QtGui, QtCore
from storage import SettingsSingleton
import functools

from utils import paths

import logging
logger = logging.getLogger(__name__)

class PreferencesDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(paths.get_ui_filepath("preferences_dialog.ui"), self)
        self.setWindowIcon(QtGui.QIcon(paths.get_art_filepath("monal_log_viewer.png")))

        self._createUiTab_color()
        self._createUiTab_misc()

    def _createUiTab_color(self):
        self.uiTab_colorWidgetList = []
        for colorIndex in range(len(SettingsSingleton().data["color"])):
            colorSection = QtWidgets.QHBoxLayout()
            color = list(SettingsSingleton().data["color"].keys())[colorIndex]
            label = QtWidgets.QLabel(self)
            label.setText(color)
            colorSection.addWidget(label)

            for position in range(len(SettingsSingleton().data["color"][color].keys())):
                colorSection.addWidget(self._createColorButton(colorIndex, position))

            self.uiGridLayout_colorTab.addLayout(colorSection)
            self.uiTab_colorWidgetList.append(colorSection)

    def _createColorButton(self, column, row):
        button = QtWidgets.QPushButton(self.uiTab_color)
        entry = SettingsSingleton().data["color"][list(SettingsSingleton().data["color"].keys())[column]]["data"][row]
        if entry != None:
            backgroundColor = "rgb("+ str(entry).replace("[", "").replace("]", "") + ")"
            r, g, b = entry
            foregroundColor = "rgb("+ str(self.get_luminance(r, g, b)).replace("[", "").replace("]", "") +")"
            button.setText(backgroundColor)
            button.setStyleSheet("background-color:"+backgroundColor+"; color: "+foregroundColor+"")
        else:
            button.setText("Add")
        button.clicked.connect(functools.partial(self._openColorPicker, column, row))
        button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(functools.partial(self._deleteColor, column, row))
        button.show()
        return button
    
    def _openColorPicker(self, column, row):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self._setColor(column, row, color.name())

    def _deleteColor(self, column, row):
        self._setColor(column, row, None)

    def _setColor(self, column, row, color=None):
        name = list(SettingsSingleton().data["color"].keys())[column]
        colorRange = SettingsSingleton().getCssColorTuple(name)
        colorRange[row] = color
        SettingsSingleton().setCssTuple(name, colorRange)
        layout = self.uiTab_colorWidgetList[column]
        itemToChange = layout.takeAt(row+1)
        layout.removeItem(itemToChange)
        layout.insertWidget(row+1, self._createColorButton(column,row))

    # see https://stackoverflow.com/a/3943023
    def get_luminance(self, r, g, b):
        colors = []
        for c in (r, g, b):
            c = c / 255.0
            if c <= 0.04045:
                c = c/12.92
            else:
                c = ((c+0.055)/1.055) ** 2.4
            colors.append(c)
        if 0.2126 * colors[0] + 0.7152 * colors[1] + 0.0722 * colors[2] > 0.179:
            return [0, 0, 0]
        return [255, 255, 255]
    
    def _createUiTab_misc(self):
        self.uiTab_miscWidgetList = []
        for entry in SettingsSingleton().data["misc"]:
            miscSection = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel()
            label.setText(entry)
            miscSection.addWidget(label)
            miscSection.addWidget(self._createMiscItems(SettingsSingleton().data["misc"][entry], entry))

            self.uiGridLayout_miscTab.addLayout(miscSection)
            self.uiTab_colorWidgetList.append(miscSection)
                
    def _createMiscItems(self, item, entry):
        if type(item) == int:
            widget = QtWidgets.QSpinBox()
            widget.setMaximum(170)
            widget.setValue(item)

        if type(item) == str:
            widget = QtWidgets.QLineEdit()
            widget.insert(item)

        if type(item) == bool:
            widget = QtWidgets.QCheckBox()
            widget.setChecked(item)

        widget.valueChanged.connect(functools.partial(self.miscWidgetClicked, widget, entry))
        return widget

    def miscWidgetClicked(self, widget, name):
        if str(type(widget)) == "<class 'PyQt5.QtWidgets.QSpinBox'>":
            SettingsSingleton().storeMisc(widget.value(), name)
        if str(type(widget)) == "<class 'PyQt5.QtWidgets.QLineEdit'>":
            SettingsSingleton().storeMisc(widget.text(), name)
        if str(type(widget)) == "<class 'PyQt5.QtWidgets.QCheckBox'>":
            SettingsSingleton().storeMisc(widget.isChecked(), name)