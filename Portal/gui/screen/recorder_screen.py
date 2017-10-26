import datetime

from PyQt4 import QtGui
from PyQt4.QtGui import *

import gui.manager
from gui.screen.abstract_screen import AbstractScreen
from PyQt4 import QtCore
import service.data.connection
import service.data.disk

from gui.screen.option_menu import OptionMenu


class RecorderScreen(AbstractScreen):
    initialized = False
    btn_recording = None  # type: QPushButton
    _is_recording = False
    _instance = None
    sender = None

    def __init__(self):
        super(RecorderScreen, self).__init__("Recording")
        RecorderScreen._instance = self
        RecorderScreen.sender = gui.manager.GenericSender("refresh_screen")
        self.connect_slots(RecorderScreen.sender)

    def initUI(self):
        super(RecorderScreen, self).initUI()

        super(RecorderScreen, self).add_button("Stop recording", 0, 0,
                                               RecorderScreen.options_handler)

    @staticmethod
    def options_handler():
        manager = gui.manager.GUIManager.get_instance()  # type: gui.manager.GUIManager
        manager.current_window.hide()
        manager.current_window = gui.screen.main_menu.MainMenu()
        manager.current_window.show()

    def connect_slots(self, sender):
        self.connect(sender, QtCore.SIGNAL('refresh_screen'),
                     self.update_background)

    def update_background(self):
        sheets = [
            "background:#F00",
            "background:#000"
        ]
        self.setStyleSheet(sheets[int((self.frame % 30) / 15)])

    def refresh(self):
        if RecorderScreen.sender is not None:
            RecorderScreen.sender.start()
        self.frame += 1
