from typing import List
import service.data.disk
import os
import service.data.connection
from service.sensor_manager import SensorType, SensorManager
from typing import Dict


# currrent_speed = config.get_setting("recording.speed", 300)



class SensorDetails:
    def __init__(self, sensor_type: SensorType, name: str, device: str,
                 settings: Dict):
        # Sensor name
        # Sensor type
        # Sensor settings
        self._device = device
        self._name = name
        self._sensor_type = sensor_type
        self._settings = settings
        if not isinstance(self._settings, Dict):
            self._settings = {}

    @property
    def device(self):
        return self._device

    @property
    def name(self):
        return self._name

    @property
    def sensor_type(self):
        return self._sensor_type

    @property
    def settings(self):
        return self._settings


class RecordDetails:
    def __init__(self, sensor_details: List[SensorDetails]):
        self._sensor_details = sensor_details

    @property
    def sensor_details(self):
        return self._sensor_details


class Recording:
    def __init__(self, mount: str, name: str, size_in_bytes: int, path: str,
                 recording_details=None):
        self._path = path
        self._size_in_bytes = size_in_bytes
        self._name = name
        self._mount = mount
        self._record_details = recording_details

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
        return self._record_details


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

    def new_recording(self):
        config = service.data.connection.Connection.get_instance()  # type: service.data.connection.Connection
        mount = config.get_setting("recording.location", "/")
        name = "NOT IMPLEMENTED"
        size_in_bytes = 0
        path = mount + "/MonitoringBox_recordings/" + name
        sensor_details = []
        manager = SensorManager.get_instance()
        manager.get_available_devices()
        for sensor in SensorManager.sensors:
            sensor_type = sensor.sensor_type
            name = sensor.name
            device = sensor.device
            settings = {}

            detail = SensorDetails(sensor_type, name, device, settings)
            sensor_details.append(detail)
        recording_details = RecordDetails(sensor_details)

        return Recording(mount, name, size_in_bytes, path, recording_details)

    def start_recording(self, recording: Recording):
        pass


import os


def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size
