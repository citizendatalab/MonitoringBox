import threading
from typing import Dict
import os



class Connection:
    SETTINGS_FILE = "./hallo"
    # Will store the singleton here.
    __instance = None

    @staticmethod
    def get_instance():
        """
        Will return the manager instance.

        :return: The manager instance.
        """
        if Connection.__instance is None:
            Connection()
        return Connection.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Connection.__instance is not None:
            raise Exception("Only one instance of the connection should exist!")
        else:
            Connection.__instance = self
        self._settings = {}  # type: Dict[str,any]
        self._lock = threading.Lock()  # type: threading.Lock

    def _load_settings_from_disk(self):
        if not self._settings:
            contents = None
            with open(Connection.SETTINGS_FILE, "r") as file:
                a = file.readlines()
                print(a)

    def _write_settings_to_disk(self):
        if self._settings:
            raise NotImplemented()

    def get_setting(self, name):
        self._lock.acquire()
        self._load_settings_from_disk()

        content = None
        if name in self._settings:
            content = self._settings[name]

        self._lock.release()
        if content is None:
            raise Exception("Couldn't find setting")
        else:
            return content
Connection().get_setting("asd")