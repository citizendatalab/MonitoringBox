import subprocess

from PyQt4 import QtGui
from PyQt4.QtCore import QSize
from PyQt4.QtGui import *

import gui.manager
from gui.screen.abstract_screen import AbstractScreen
from PyQt4 import QtCore

import gui.screen.main_menu
import gui.screen.option_menu
from service.sensor_manager import SensorManager


class SensorList(AbstractScreen):
    btn_recording = None  # type: QPushButton
    _is_recording = False
    list_widget = None

    def __init__(self):
        super(SensorList, self).__init__("Main menu")

    def initUI(self):
        super(SensorList, self).initUI()
        SensorList.btn_recording = super(SensorList, self).add_button(
            "Back",
            0, 0, SensorList.main_menu_handler)
        self.show()

    def before_vertical_layout(self, vbox):
        label = QLabel("MonitoringBox")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setFont(QtGui.QFont('Decorative', 20))
        label.setStyleSheet("color:#FFF")
        vbox.addWidget(label, 1)

        font = QtGui.QFont('Decorative', 10)
        font.setItalic(True)

        self.list_widget = QListWidget()

        self.list_widget.setStyleSheet(
            "QListWidget{background:#777; color:#EEE; border:none} QListWidget:item:selected:active{background:auto;color:auto;}QListWidget:item{border-radius: 0 !important;}" +
            "QScrollBar:vertical {"
            "    border: 1px solid #999999;"
            "    background:white;"
            "    width:10px;"
            "    margin: 0px 0px 0px 0px;"
            "}"
            "QScrollBar::handle:vertical {"
            "    background: #444;"
            "    min-height: 0px;"
            "}"
            "QScrollBar::add-line:vertical {"
            "    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            "    stop: 0 rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));"
            "    height: 0px;"
            "    subcontrol-position: bottom;"
            "    subcontrol-origin: margin;"
            "}"
            "QScrollBar::sub-line:vertical {"
            "    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            "    stop: 0  rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));"
            "    height: 0 px;"
            "    subcontrol-position: top;"
            "    subcontrol-origin: margin;"
            "}")
        size = QSize()
        size.expandedTo(self.list_widget.size())
        size.setHeight(28)

        sensor_manager = SensorManager.get_instance()  # type: SensorManager
        for device_name in sensor_manager.get_sensor_devices():
            sensor = sensor_manager.get_sensor_by_device(device_name)
            item = QListWidgetItem(
                str(
                    sensor.sensor_type.value) + " - " + sensor.name + " (" + device_name + ")")
            item.setSizeHint(size)
            self.list_widget.addItem(item)
        vbox.addWidget(self.list_widget)

    @staticmethod
    def main_menu_handler():
        manager = gui.manager.GUIManager.get_instance()  # type: gui.manager.GUIManager
        manager.current_window.hide()
        manager.current_window = gui.screen.option_menu.OptionMenu()
        manager.current_window.show()
