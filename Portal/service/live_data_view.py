import threading
from typing import List

import time
import service.data.connection
from service.sensor.communicator.communicators import get_communicator_instance
from service.sensor_manager import Sensor


class LiveView:
    def __init__(self, sensor: Sensor):
        self.sensor = sensor
        self._data = []
        self.last_insert_check = -1

    @property
    def data(self) -> List[any]:
        return self._data

    def add_data(self, new_data):
        self._data.append(new_data)
        if len(self._data) > 25:
            try:
                self._data.pop(0)
            except Exception as ex:
                a=1


current_milli_time = lambda: int(round(time.time() * 1000))


def _live_view_callback(data, connection, callback_options):
    # lock = callback_options["lock"]  # type: threading.Lock
    live_views = callback_options["live_views"]  # type: LiveView
    # lock.release()
    live_views.add_data(data)


class LiveViewManager:
    # Will store the singleton here.
    __instance = None

    @staticmethod
    def get_instance():
        """
        Will return the manager instance.

        :return: The manager instance.
        """
        if LiveViewManager.__instance is None:
            LiveViewManager()
        return LiveViewManager.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if LiveViewManager.__instance is not None:
            raise Exception("Only one instance of the manager should exist!")
        else:
            LiveViewManager.__instance = self
        self._views = {}

    def get_data(self, sensor: Sensor) -> LiveView:
        if sensor not in self._views:
            self._views[sensor] = LiveView(sensor)
        view = self._views[sensor]
        connection = service.data.connection.Connection.get_instance()
        if view.last_insert_check < current_milli_time() - connection.get_setting("recording.speed", 300):
            view.last_insert_check = current_milli_time()
            communicator = get_communicator_instance(sensor)
            # lock = threading.Lock()
            # lock.acquire()

            # communicator.get_sensor_values(sensor, _live_view_callback,
            #                                {"lock": lock, "live_views": view})
            communicator.get_sensor_values(sensor, _live_view_callback,
                                           {"live_views": view})
            # lock.acquire()
        return view
