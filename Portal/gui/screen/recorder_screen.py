import datetime

from PyQt4 import QtGui
from PyQt4.QtGui import *

import gui.manager
from gui.screen.abstract_screen import AbstractScreen
from PyQt4 import QtCore
import service.data.connection
import service.data.disk

from gui.screen.option_menu import OptionMenu
from service.recorder.recordings_manager import Recording
from service.recorder.recordings_manager import RecordingManager
from service.sensor.communicator.communicators import \
    AbstractArduinoCommunicator
from service.sensor.communicator.communicators import get_communicator_instance
from service.sensor_manager import Sensor
from service.sensor_manager import SensorManager


class RecorderScreen(AbstractScreen):
    initialized = False
    btn_recording = None  # type: QPushButton
    _is_recording = False
    _instance = None
    sender = None
    show_data = {}
    label_sensor_name = None
    label_sensor_value = None

    def __init__(self):
        super(RecorderScreen, self).__init__("Recording")
        RecorderScreen._instance = self
        RecorderScreen.sender = gui.manager.GenericSender("refresh_screen")
        self.connect_slots(RecorderScreen.sender)
        manager = RecordingManager.get_instance()  # type: RecordingManager
        self._recording = manager.new_recording()  # type: Recording
        self._recorder = manager.start_recording(self._recording)
        self.display_sensor_index = 0

    def initUI(self):
        super(RecorderScreen, self).initUI()

        super(RecorderScreen, self).add_button("Stop recording", 0, 0,
                                               RecorderScreen.options_handler)

    @staticmethod
    def options_handler():
        record_manager = RecordingManager.get_instance()  # type: RecordingManager
        record_manager.stop_recording(RecorderScreen._instance._recorder)

        gui_manager = gui.manager.GUIManager.get_instance()  # type: gui.manager.GUIManager
        gui_manager.current_window.hide()
        gui_manager.current_window = gui.screen.main_menu.MainMenu()
        gui_manager.current_window.show()

    def before_vertical_layout(self, vbox):
        label = QLabel("Recording")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setFont(QtGui.QFont('Decorative', 18))
        label.setStyleSheet("color:#FFF")
        vbox.addWidget(label, 0)

        RecorderScreen.label_sensor_name = QLabel("Loading...")
        RecorderScreen.label_sensor_name.setAlignment(QtCore.Qt.AlignCenter)
        RecorderScreen.label_sensor_name.setFont(QtGui.QFont('Decorative', 12 ))
        RecorderScreen.label_sensor_name.setStyleSheet(
            "color:#FFF; background: #444")
        vbox.addWidget(RecorderScreen.label_sensor_name, 1)

        RecorderScreen.label_sensor_value = QLabel("Please wait...")
        RecorderScreen.label_sensor_value.setAlignment(QtCore.Qt.AlignCenter)
        RecorderScreen.label_sensor_value.setFont(QtGui.QFont('Decorative', 10))
        RecorderScreen.label_sensor_value.setStyleSheet(
            "color:#FFF; background: #444")
        vbox.addWidget(RecorderScreen.label_sensor_value, 1)

    def connect_slots(self, sender):
        self.connect(sender, QtCore.SIGNAL('refresh_screen'),
                     self.update_screen)

    def update_screen(self):
        sheets = [
            "background:#F00",
            "background:#000"
        ]
        self.setStyleSheet(sheets[int((self.frame % 30) / 15)])
        sensor_manager = SensorManager.get_instance()  # type: SensorManager
        devices = sensor_manager.get_sensor_devices()
        self.display_sensor_index = int(self.frame / 180) % (1+len(devices))

        if self.display_sensor_index == len(devices):
            label_sensor = RecorderScreen.label_sensor_name  # type: QLabel
            label_sensor.setText("Sensors connected")
            RecorderScreen.label_sensor_value.setText(str(len(devices)))
            return
        device = devices[self.display_sensor_index]
        sensor = sensor_manager.get_sensor_by_device(device)

        communicator = get_communicator_instance(
            sensor)  # type: AbstractArduinoCommunicator
        if "data" in RecorderScreen.show_data:
            data = RecorderScreen.show_data["data"]

            sensor_handler = RecorderScreen.show_data["options"][
                "sensor"]  # type: Sensor
            out = ""
            for k in data:
                out += k + ": " + data[k] + "\n"
            if len(out) > 0:
                out = out[:-1]
            RecorderScreen.label_sensor_value.setText(out)
            label_sensor = RecorderScreen.label_sensor_name  # type: QLabel
            label_sensor.setText(
                sensor_handler.name + " - " + sensor_handler.sensor_type.value)
        communicator.get_sensor_values(sensor, callback, {"sensor": sensor})

    def refresh(self):
        if RecorderScreen.sender is not None:
            RecorderScreen.sender.start()
        self.frame += 1


def callback(data, connection, callback_options):
    data = data["data"]

    for item in data:
        data[item] = str(data[item])

    RecorderScreen.show_data = {
        "data": data,
        "options": callback_options
    }
