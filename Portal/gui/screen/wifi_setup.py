import subprocess

from PyQt4 import QtGui
from PyQt4.QtGui import *

import gui.manager
from gui.screen.abstract_screen import AbstractScreen
from PyQt4 import QtCore

import gui.screen.main_menu
import gui.screen.option_menu

class WifiMenu(AbstractScreen):
    btn_recording = None  # type: QPushButton
    _is_recording = False

    def __init__(self):
        super(WifiMenu, self).__init__("Main menu")

    def initUI(self):
        super(WifiMenu, self).initUI()
        WifiMenu.btn_recording = super(WifiMenu, self).add_button(
            "Back",
            0, 0, WifiMenu.main_menu_handler)
        self.show()

    def before_vertical_layout(self, vbox):
        label = QLabel("MonitoringBox")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setFont(QtGui.QFont('Decorative', 20))
        label.setStyleSheet("color:#FFF")
        vbox.addWidget(label, 1)

        font = QtGui.QFont('Decorative', 10)
        font.setItalic(True)

        label = QLabel("W.I.P.")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setFont(font)
        label.setStyleSheet("color:#FFF")
        vbox.addWidget(label, 1)


    @staticmethod
    def main_menu_handler():
        manager = gui.manager.GUIManager.get_instance() # type: gui.manager.GUIManager
        manager.current_window.hide()
        manager.current_window = gui.screen.option_menu.OptionMenu()
        manager.current_window.show()

