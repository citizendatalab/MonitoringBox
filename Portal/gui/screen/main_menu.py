from PyQt4 import QtGui
from PyQt4.QtGui import *

import gui.manager
from gui.screen.abstract_screen import AbstractScreen
from PyQt4 import QtCore
import service.data.connection
import service.data.disk

from gui.screen.option_menu import OptionMenu
from gui.screen.recorder_screen import RecorderScreen


class MainMenu(AbstractScreen):
    initialized = False
    btn_recording = None  # type: QPushButton
    _is_recording = False
    _instance = None

    def __init__(self):
        super(MainMenu, self).__init__("Main menu")
        MainMenu._instance = self

    def initUI(self):
        super(MainMenu, self).initUI()
        MainMenu.btn_recording = super(MainMenu, self).add_button(
            "Start recording",
            0, 0, MainMenu.recording_state_handler)
        super(MainMenu, self).add_button("Options", 0, 1,
                                         MainMenu.options_handler)
        self.show()
        MainMenu.initialized = True

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

        MainMenu.progress = QtGui.QProgressBar(self)
        vbox.addWidget(MainMenu.progress, 1)

        MainMenu.storage_label = QLabel("")
        MainMenu.storage_label.setAlignment(QtCore.Qt.AlignCenter)
        MainMenu.storage_label.setFont(font)
        MainMenu.storage_label.setStyleSheet("color:#FFF")
        vbox.addWidget(MainMenu.storage_label, 1)

        MainMenu.update_disk_space()
        # MainMenu.update_progressbar(int(
        #     round(mount.get_dict()["percent_usage"], 0)), 100, "")

    @staticmethod
    def update_disk_space():
        config = service.data.connection.Connection.get_instance()  # type: service.data.connection.Connection
        location = config.get_setting("recording.location", "/")
        mount = None
        try:
            mount = service.data.disk.get_mount(location)
        except:
            location = "/"
            mount = service.data.disk.get_mount(location)
        MainMenu.update_progressbar(int(
            round(mount.get_dict()["percent_usage"], 0)), 100, location)

    @staticmethod
    def update_progressbar(value: int, max: int, location: str):
        MainMenu.progress.setValue(value)
        MainMenu.progress.setMaximum(max)
        percent = (int)(255 * (value / max))
        color_r = '{:02x}'.format(percent)
        color_b = '{:02x}'.format(255 - percent)
        MainMenu.progress.setStyleSheet("" +
                                        "QProgressBar{"
                                        "border: none;"
                                        "text-align: center;"
                                        "background: #555;"
                                        "color:#FFF;"
                                        "font-weight:bold"
                                        "}"

                                        "QProgressBar::chunk {"
                                        "background-color: #" + str(
            color_r) + "00" + str(color_b) + ";"
                                             "}")
        MainMenu.storage_label.setText(location)

    @staticmethod
    def recording_state_handler():
        manager = gui.manager.GUIManager.get_instance()  # type: gui.manager.GUIManager
        manager.current_window.hide()
        manager.current_window = RecorderScreen()
        manager.current_window.show()

        # MainMenu.btn_recording.setText(
        #     ["Stop recording", "Start recording"][MainMenu._is_recording])
        # MainMenu._is_recording = not MainMenu._is_recording
        # import random
        # MainMenu.update_progressbar(random.randrange(0, 100), 100, "")

    @staticmethod
    def options_handler():
        manager = gui.manager.GUIManager.get_instance()  # type: gui.manager.GUIManager
        manager.current_window.hide()
        manager.current_window = OptionMenu()
        manager.current_window.show()

    def connect_slots(self, sender):
        self.connect(sender, QtCore.SIGNAL('recording.location_update'), self.say_hello)

    def say_hello(self):
        MainMenu.update_disk_space()


class _Sender(QtCore.QThread):
    def run(self):
        self.emit(QtCore.SIGNAL('recording.location_update'))


def disk_change_handler(value):
    if MainMenu.initialized:
        sender = _Sender()
        main_menu = MainMenu._instance  # type: MainMenu
        main_menu.connect_slots(sender)
        sender.start()


service.data.connection.Connection.get_instance().register_on_change_listener(
    "recording.location", disk_change_handler)
