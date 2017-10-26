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
        self._listeners = {}

    def register_on_change_listener(self, setting_name: str, listener):
        if setting_name not in self._listeners:
            self._listeners[setting_name] = []
        self._listeners[setting_name].append(listener)

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

        if name in self._listeners:
            for listener in self._listeners[name]:
                listener(value)

    def _write_settings_to_disk(self):
        """
        Will write all settings to disk.
        """
        with open(Connection.SETTINGS_FILE, "w") as file:
            json.dump(self._settings, file)

    def get_setting(self, name: str, default=None) -> any:
        """
        Will get the setting with given name.

        :param name: Name of the setting.
        :param default: The default value, if None was it throws an exception when not found.
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

        # If nothing was found throw an exception or set a default value.
        if content is None:
            if default is None:
                raise Exception("Couldn't find setting")
            else:
                content = default

        return content
