import threading
from typing import Dict
import json


class Connection:
    """
    The location of the user settings
    """
    SETTINGS_FILE = "/var/opt/monitoringbox/config.json"

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
        """
        Loads the settings from disk into the settings field.
        """
        if not self._settings:
            with open(Connection.SETTINGS_FILE, "r") as file:
                self._settings = json.load(file)

    def put_setting(self, name: str, value: any):
        """
        Will store the setting.

        :param name: Name of the setting.
        :param value: Value of the setting.
        """
        # Will lock the object.
        self._lock.acquire()
        self._load_settings_from_disk()

        # Save the setting.
        self._settings[name] = value
        self._write_settings_to_disk()

        # Will make the object available again.
        self._lock.release()

    def _write_settings_to_disk(self):
        """
        Will write all settings to disk.
        """
        with open(Connection.SETTINGS_FILE, "w") as file:
            json.dump(self._settings, file)

    def get_setting(self, name: str) -> any:
        """
        Will get the setting with given name.

        :param name: Name of the setting.
        :raises Exception: When it couldn't find the setting.
        :return: The value of the setting.
        """
        # Will lock the object
        self._lock.acquire()
        self._load_settings_from_disk()

        # Get the content of the given setting.
        content = None
        if name in self._settings:
            content = self._settings[name]

        # Will make the object available again.
        self._lock.release()

        # If we didn't find the thing we're looking for, raise an error else
        # just return it.
        if content is None:
            raise Exception("Couldn't find setting")
        else:
            return content
