from PyQt4 import QtGui
from PyQt4.QtGui import *

import gui.manager
from gui.screen.abstract_screen import AbstractScreen
from PyQt4 import QtCore

import gui.screen.main_menu
import gui.screen.wifi_setup
import gui.screen.sensor_list
import service.device_options


class OptionMenu(AbstractScreen):
    btn_recording = None  # type: QPushButton
    _is_recording = False

    def __init__(self):
        super(OptionMenu, self).__init__("Main menu")

    def initUI(self):
        super(OptionMenu, self).initUI()
        OptionMenu.btn_recording = super(OptionMenu, self).add_button(
            "Back",
            0, 0, OptionMenu.main_menu_handler)
        super(OptionMenu, self).add_button("Wifi setup", 0, 1,
                                           OptionMenu.wifi_setup_handler)
        super(OptionMenu, self).add_button("Sensors", 1, 0,
                                           OptionMenu.sensor_handler)
        super(OptionMenu, self).add_button("Shutdown", 1, 1,
                                           OptionMenu.shutdown_handler)
        self.show()

    def before_vertical_layout(self, vbox):
        label = QLabel("MonitoringBox")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setFont(QtGui.QFont('Decorative', 20))
        label.setStyleSheet("color:#FFF")
        vbox.addWidget(label, 1)

        font = QtGui.QFont('Decorative', 10)
        font.setItalic(True)

        label = QLabel("All sensor initialized")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setFont(font)
        label.setStyleSheet("color:#FFF")
        vbox.addWidget(label, 1)

    @staticmethod
    def main_menu_handler():
        manager = gui.manager.GUIManager.get_instance()  # type: gui.manager.GUIManager
        manager.current_window.hide()
        manager.current_window = gui.screen.main_menu.MainMenu()
        manager.current_window.show()

    @staticmethod
    def shutdown_handler():
        service.device_options.shutdown()

    @staticmethod
    def wifi_setup_handler():
        manager = gui.manager.GUIManager.get_instance()  # type: gui.manager.GUIManager
        manager.current_window.hide()
        manager.current_window = gui.screen.wifi_setup.WifiMenu()
        manager.current_window.show()

    @staticmethod
    def sensor_handler():
        manager = gui.manager.GUIManager.get_instance()  # type: gui.manager.GUIManager
        manager.current_window.hide()
        manager.current_window = gui.screen.sensor_list.SensorList()
        manager.current_window.show()
