import threading
import sys
import time
from PyQt4 import QtGui
from PyQt4 import QtCore


from gui.screen.main_menu import MainMenu

app = QtGui.QApplication(sys.argv)


class GUIManager:
    # Will store the singleton here.
    __instance = None

    @staticmethod
    def get_instance():
        """
        Will return the manager instance.

        :return: The manager instance.
        """
        if GUIManager.__instance is None:
            GUIManager()
        return GUIManager.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if GUIManager.__instance is not None:
            raise Exception("Only one instance of the connection should exist!")
        else:
            GUIManager.__instance = self
        self.title = ""
        self.current_window = None
        # window = Window()
        # sys.exit(app.exec_())

    #         self.current_widget = None
    #         self.title = ""
    #         # self.app = None
    #
    def start(self):
        FrameCounter().start()

        time.sleep(4)

        self.current_window.hide()
        self.current_window = MainMenu()

        sys.exit(app.exec_())

    def _refresh(self):
        if hasattr(self.current_window, 'refresh'):
            self.current_window.refresh()


class FrameCounter(threading.Thread):
    def run(self):
        while True:
            time.sleep(1 / 30)
            GUIManager.get_instance()._refresh()


class GenericSender(QtCore.QThread):
    def __init__(self, signal: str):
        super(GenericSender, self).__init__()
        self._signal = signal

    def run(self):
        self.emit(QtCore.SIGNAL(self._signal))
