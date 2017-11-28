import json
import threading
from typing import List
import datetime

import time
from  service.sensor.communicator import communicators
import service.data.disk
import os
import service.data.connection
from service.sensor.communicator.communicators import AbstractCommunicator
from service.sensor.communicator.communicators import get_communicator_instance
from service.sensor_manager import SensorType, SensorManager, Sensor
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

    def as_dict(self):
        return {
            "name": self.name,
            "device": self.device,
            "sensor_type": self.sensor_type.name,
            "settings": self.settings
        }

    @staticmethod
    def from_dict(data: dict):
        return SensorDetails(
            SensorType.from_string(data["sensor_type"]),
            data["name"],
            data["device"],
            data["settings"]
        )


class RecordDetails:
    def __init__(self, sensor_details: List[SensorDetails]):
        self._sensor_details = sensor_details

    @property
    def sensor_details(self):
        return self._sensor_details

    def as_dict(self):
        details = []
        for sensor in self._sensor_details:
            details.append(sensor.as_dict())
        return {
            "sensor_details": details
        }

    @staticmethod
    def from_dict(data: dict):
        details = []
        for sensor in data["sensor_details"]:
            details.append(SensorDetails.from_dict(sensor))
        return RecordDetails(details)


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

    @property
    def path(self):
        return self._path

    def as_dict(self):
        details = None
        if self.record_details is not None:
            details = self.record_details.as_dict()
        return {
            "size_in_bytes": self.size_in_bytes,
            "name": self.name,
            "mount": self.mount,
            "record_details": details,
            "path": self.path
        }

    @staticmethod
    def from_dict(data: Dict):
        details = None
        if data["record_details"] is not None:
            details = RecordDetails.from_dict(data["record_details"])
        return Recording(data["mount"], data["name"], data["size_in_bytes"],
                         data["path"], details)


# callback_options["callback"](data, connection, callback_options["options"])
def _sensor_value_callback(data, connection, callback_options):
    cycle = callback_options["cycle"]
    sensor = callback_options["sensor"]
    recording = callback_options["recording"]
    manager = RecordingManager.get_instance()  # type: RecordingManager
    value = data
    manager._register_record(recording, cycle, sensor, value)


class Recorder(threading.Thread):
    def __init__(self, recording: Recording):
        super(Recorder, self).__init__()
        self.keep_running = True
        self._cycle = 0
        self._recording = recording

    def _get_sensors(self):
        manager = SensorManager.get_instance()
        sensors = []
        for device in manager.get_sensor_devices():
            sensors.append(manager.get_sensor_by_device(device))
        return sensors

    def _get_sensor_communicators(self) -> List[
        Dict[str, AbstractCommunicator]]:
        sensors = self._get_sensors()
        communicators = []
        for sensor in sensors:
            communicators.append({
                "sensor": sensor,
                "communicator": get_communicator_instance(sensor),
                "recording": self._recording
            })
        return communicators

    def run(self):
        config = service.data.connection.Connection.get_instance()  # type: service.data.connection.Connection
        delay = config.get_setting("recording.speed", 300)

        communicator_list = self._get_sensor_communicators()
        last_run = datetime.datetime.now()

        while self.keep_running:
            for communicator in communicator_list:
                sensor = communicator["sensor"]
                communicator = communicator["communicator"]
                communicator.get_sensor_values(sensor, _sensor_value_callback, {
                    "cycle": self._cycle,
                    "sensor": sensor,
                    "recording": self._recording
                })
            self._cycle += 1
            last_run_temp = datetime.datetime.now()
            wait_time = delay - ((last_run_temp - last_run).microseconds / 1000)
            last_run = last_run_temp
            time.sleep(wait_time / 1000)


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
        self._lock = threading.Lock()  # type: threading.Lock
        self._recording_lock = {}  # type: Dict[str, threading.Lock]

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
        now = datetime.datetime.now()

        name = str(now.year) + "-" + str(now.month) + "-" + str(
            now.day) + " " + str(now.hour) + "." + str(now.minute)
        size_in_bytes = 0
        path = mount + "/MonitoringBox_recordings/" + name
        sensor_details = []
        manager = SensorManager.get_instance()
        for sensor in manager.sensors:
            sensor_type = manager.sensors[sensor].sensor_type
            name = manager.sensors[sensor].name
            device = manager.sensors[sensor].device
            settings = {}

            detail = SensorDetails(sensor_type, name, device, settings)
            sensor_details.append(detail)
        recording_details = RecordDetails(sensor_details)

        return Recording(mount, name, size_in_bytes, path, recording_details)

    def _lock_writer(self, sensor: Sensor):
        self._lock.acquire()
        if sensor.device not in self._recording_lock:
            self._recording_lock[sensor.device] = threading.Lock()
        self._lock.release()
        self._recording_lock[sensor.device].acquire()

    def _release(self, sensor: Sensor):
        self._recording_lock[sensor.device].release()

    def _setup_recording_information(self, recording: Recording):
        if not os.path.exists(recording.path):
            os.mkdir(recording.path)

        info_path = recording.path + "/recording.json"

        if not os.path.exists(info_path):
            with open(info_path, "w") as file:
                temp = json.dumps(recording.as_dict())
                file.write(temp)

        for detail in recording.record_details.sensor_details:
            if not os.path.exists(
                                    recording.path + "/" + detail.sensor_type.name):
                os.mkdir(recording.path + "/" + detail.sensor_type.name)

    def get_recording(self, path: str) -> Recording:
        info_path = path + "/recording.json"
        if os.path.exists(info_path):
            data = {}
            with open(info_path, "r") as file:
                raw = "\n".join(file.readlines())
                data = json.loads(raw)
            return Recording.from_dict(data)
        else:
            raise FileNotFoundError()

    def _register_record(self, recording: Recording, cycle: int, sensor: Sensor,
                         value: any):
        self._lock_writer(sensor)
        self._setup_recording_information(recording)

        with open(
                                                        recording.path + "/" + sensor.sensor_type.name + "/" + sensor.device.replace(
                            "/", "_") + ".dat", "a+") as file:
            file.write(json.dumps({"cycle": cycle, "data": value}) + "\n")
            file.close()
        self._release(sensor)

    def start_recording(self, recording: Recording) -> Recorder:
        recorder = Recorder(recording)
        recorder.start()
        return recorder

    def stop_recording(self, recorder: Recorder):
        recorder.keep_running = False


import os


def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size
