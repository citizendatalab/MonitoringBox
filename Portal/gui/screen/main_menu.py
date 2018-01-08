from PyQt4 import QtGui
from PyQt4.QtGui import *

import gui.manager
from gui.screen.abstract_screen import AbstractScreen
from PyQt4 import QtCore
import service.data.connection
import service.data.disk

from gui.screen.option_menu import OptionMenu
from gui.screen.recorder_screen import RecorderScreen
from service.sensor_manager import SensorManager, Sensor


class MainMenu(AbstractScreen):
    initialized = False
    btn_recording = None  # type: QPushButton
    _is_recording = False
    _instance = None
    sender = None
    _informer_registered = False
    label = None
    sender_sensor_update = None
    enable_recording = True

    def __init__(self):
        super(MainMenu, self).__init__("Main menu")
        MainMenu._instance = self
        MainMenu.sender = gui.manager.GenericSender("recording.location_update")
        self.connect_slots(MainMenu.sender)
        MainMenu.sender_sensor_update = gui.manager.GenericSender(
            "sensors.update")
        self.connect_slots(MainMenu.sender_sensor_update)

        if not MainMenu._informer_registered:
            manager = SensorManager.get_instance()  # type: SensorManager
            manager.add_informer(MainMenu.sensor_update_informer)

    @staticmethod
    def sensor_update_informer(sensor: Sensor):
        from gui.manager import GUIManager
        gui_manager = GUIManager.get_instance()  # type: GUIManager
        if gui_manager.current_window == MainMenu._instance:
            if MainMenu.label is not None:
                MainMenu.update_connected_sensor_text()
            if MainMenu.btn_recording is not None:
                sensor_manager = SensorManager.get_instance()  # type: SensorManager
                MainMenu.enable_recording = sensor_manager.sensor_count > 0
                MainMenu.sender_sensor_update.start()

    @staticmethod
    def update_connected_sensor_text():
        sensor_manager = SensorManager.get_instance()  # type: SensorManager
        MainMenu.label.setText(str(sensor_manager.sensor_count) + " " + (
            ["sensors", "sensor"][
                sensor_manager.sensor_count == 1]) + " connected, disk usage:")

    def initUI(self):
        super(MainMenu, self).initUI()
        MainMenu.btn_recording = super(MainMenu, self).add_button(
            "Start recording",
            0, 0, MainMenu.recording_state_handler)
        sensor_manager = SensorManager.get_instance()  # type: SensorManager
        MainMenu.enable_recording = sensor_manager.sensor_count > 0
        self.update_recording_button()
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

        MainMenu.label = QLabel("0 sensors connected, disk usage:")
        MainMenu.label.setAlignment(QtCore.Qt.AlignCenter)
        MainMenu.label.setFont(font)
        MainMenu.label.setStyleSheet("color:#FFF")
        vbox.addWidget(MainMenu.label, 1)
        MainMenu.update_connected_sensor_text()

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
        self.connect(sender, QtCore.SIGNAL('recording.location_update'),
                     self.say_hello)

        self.connect(sender, QtCore.SIGNAL('sensors.update'),
                     self.update_recording_button)

    def update_recording_button(self):
        MainMenu.btn_recording.setEnabled(MainMenu.enable_recording)
        MainMenu.btn_recording.setStyleSheet(
            "background:#" + (["AAA", "EEE"][
                                  MainMenu.enable_recording]) + "; border:#000; color:#000; padding:1em")

    @staticmethod
    def disk_space_update():
        MainMenu.sender.start()

    def say_hello(self):
        MainMenu.update_disk_space()


def disk_change_handler(value):
    if MainMenu.initialized:
        MainMenu.disk_space_update()


service.data.connection.Connection.get_instance().register_on_change_listener(
    "recording.location", disk_change_handler)
