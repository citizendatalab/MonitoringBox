from typing import List
import service.data.disk
import os

from service.sensor_manager import SensorType


class Recording:
    def __init__(self, mount: str, name: str, size_in_bytes: int, path: str):
        self._path = path
        self._size_in_bytes = size_in_bytes
        self._name = name
        self._mount = mount
        self._record_details = None

    @property
    def size_in_bytes(self):
        return self._size_in_bytes

    @property
    def name(self):
        return self._name

    @property
    def mount(self):
        return self._mount

    @property
    def record_details(self) -> RecordDetails:
        if self._record_details is None:
            #Load
        return self._record_details


class RecordDetails:
    def __init__(self, sensor_details: List[SensorDetails]):
        self._sensor_details = sensor_details

    @property
    def sensor_details(self):
        return self._sensor_details


class SensorDetails:
    def __init__(self, sensor_type: SensorType, name: str, device: str):
        # Sensor name
        # Sensor type
        # Sensor settings
        self._device = device
        self._name = name
        self._sensor_type = sensor_type

    @property
    def device(self):
        return self._device

    @property
    def name(self):
        return self._name

    @property
    def sensor_type(self):
        return self._sensor_type


class RecordingManager:
    # Will store the singleton here.
    __instance = None

    @staticmethod
    def get_instance():
        """
        Will return the manager instance.

        :return: The manager instance.
        """
        if RecordingManager.__instance is None:
            RecordingManager()
        return RecordingManager.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if RecordingManager.__instance is not None:
            raise Exception("Only one instance of the manager should exist!")
        else:
            RecordingManager.__instance = self

    def list_recordings(self) -> List[Recording]:

        recordings = []
        for mount in service.data.disk.get_mounts():
            # mount.mount_point
            path = mount.mount_point + "/MonitoringBox_recordings"
            if os.path.exists(path):
                folders = os.listdir(
                    mount.mount_point + "/MonitoringBox_recordings")
                for folder in folders:
                    recordings.append(Recording(mount.mount_point, folder,
                                                get_size(path + "/" + folder),
                                                path + "/" + folder))

        return recordings


import os


def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size
