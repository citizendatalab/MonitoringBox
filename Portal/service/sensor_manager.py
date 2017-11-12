from enum import Enum
from typing import List, Dict
import threading
import service.serial.manager
import time
from service.sensor.handler_watcher import HandlerWatcher
from service.sensor.handlers.abstract_handler import AbstractHandler
import json


class SensorType(Enum):
    """
    Defines a sensor type.
    """
    UNKOWN = "unkown sensor"
    EXAMPLE_SENSOR = "example sensor"
    PI_CAMERA = "Picam"
    GPS_SENSOR = "GPS sensor"
    HUMIDITY_TEMPERATURE_SENSOR = "humidity temperature sensor"
    CO2_SENSOR = "CO2 sensor"
    HEART_RATE_SENSOR = "Heart rate sensor"
    GALVANIC_SKIN_RESPONSE_SENSOR = "Galvanic skin response sensor"

    @staticmethod
    def from_string(type: str):
        types = {
            "UNKOWN": SensorType.UNKOWN,
            "EXAMPLE_SENSOR": SensorType.EXAMPLE_SENSOR,
            "PI_CAMERA": SensorType.PI_CAMERA,
            "GPS_SENSOR": SensorType.GPS_SENSOR,
            "Temperature and Humidity": SensorType.HUMIDITY_TEMPERATURE_SENSOR,
            "CO2": SensorType.CO2_SENSOR,
            "HEART_RATE_SENSOR": SensorType.HEART_RATE_SENSOR,
            "GALVANIC_SKIN_RESPONSE_SENSOR": SensorType.GALVANIC_SKIN_RESPONSE_SENSOR
        }
        if type in types:
            return types[type]
        else:
            return SensorType.UNKOWN


class HandlerTrigger:
    """
    Defines when a sensor will trigger a handler.
    """

    def __init__(self, sensor_types: List[SensorType], sensor_names: List[str],
                 any_field_match: bool):
        self._any_field_match = any_field_match
        self._sensor_types = sensor_types  # type: List[SensorType]
        self._sensor_names = sensor_names  # type: List[str]

    @property
    def any_field_match(self):
        """
        If any or all fields need to have a match before triggering.

        :return: True if any can match (so one or more matches).
        """
        return self._any_field_match

    @property
    def sensor_types(self) -> List[SensorType]:
        """
        :return: the sensor types it needs to response on.
        """
        return self._sensor_types

    @property
    def sensor_names(self) -> List[str]:
        """
        :return: The sensor names the sensor needs to react on.
        """
        return self._sensor_names


class Sensor:
    """
    Defines a sensor.
    """

    def __init__(self, sensor_type: SensorType, name: str, device: str,
                 connection: service.serial.manager.SerialConnection):
        self._connection = connection
        self._device = device
        self._sensor_type = sensor_type
        self._name = name
        self._did_receive_first_packet = False

    def received_first_packet(self):
        self._did_receive_first_packet = True

    @property
    def first_packet_received(self) -> bool:
        return self._did_receive_first_packet

    @property
    def connection(self):
        """
        :return: The connection to the sensor.
        """
        return self._connection

    @property
    def device(self):
        """
        :return: The device path the sensor is on.
        """
        return self._device

    @property
    def sensor_type(self):
        """
        :return: The type of the sensor.
        """
        return self._sensor_type

    @sensor_type.setter
    def sensor_type(self, value: SensorType):
        self._sensor_type = value

    @property
    def name(self):
        """
        :return: The name of the sensor.
        """
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value


def _sensor_disconnect_listener(
        connection: service.serial.manager.SerialConnection):
    """
    Will be called when a sensor disconnects from the platform.

    :param connection: The connection that was disconnected.
    """
    # Get the sensor.
    sensor_manager = SensorManager.get_instance()  # type: SensorManager
    sensor = sensor_manager.get_sensor_by_device(
        connection.device)  # type: Sensor

    # Tell the sensor manager that the sensor isn't connected anymore.
    sensor_manager._deregister_sensor(sensor)


def _sensor_line_listener(
        connection: service.serial.manager.SerialConnection, line: str):
    """
    Will be called when a sensor recieves data.

    :param connection: The connection on which the data was received.
    :param line: The line that was received.
    """
    manager = SensorManager.get_instance()  # type: SensorManager
    manager._trigger_type_handlers(connection.device, line)


def _update_information(data, connection: service.serial.manager.SerialConnection, callback_options):
    sensor_manager = SensorManager.get_instance()  # type: SensorManager
    sensor = sensor_manager.get_sensor_by_device(connection.device)
    sensor.name = data["name"]
    sensor.sensor_type = SensorType.from_string(data["sensor"])


class _SensorSearcher(threading.Thread):
    """
    Thread that will continuously search for sensors, these sensors will
    automatically be registered to the sensor manager. If a sensor is removed
    it will deregister the sensor in the manager.
    """

    """
    Will make sure that only one instance of this thread can run at a time.
    """
    _is_running = False

    def run(self):
        """
        Handles running the thread.
        """

        # Stop the thread if it is already running.
        if _SensorSearcher._is_running:
            return

        # Setup for searching the sensors.
        _SensorSearcher._is_running = True
        manager = service.serial.manager.Manager.get_instance()  # type: Manager
        sensor_manager = SensorManager.get_instance()  # type: SensorManager

        # Keep running the thread until it needs to stop.
        while _SensorSearcher._is_running:
            # It can happen that there is a error reading the connected serial
            # devices, if so just ignore it because we already know the
            # connected devices. And if a device was removed, it will be solved
            # next loop iteration.
            try:
                # Get the old and new devices.
                available_devices = set(manager.get_available_devices())
                known_devices = set(sensor_manager.get_sensor_devices())
                old_devices = set(known_devices - available_devices)
                new_devices = set(available_devices - known_devices)

                for device in old_devices:
                    if sensor_manager.get_sensor_by_device(
                            device).sensor_type != SensorType.PI_CAMERA:
                        self._deregister_device(device)
                if new_devices:
                    # Sleep sometime because the serial connection needs some
                    # initialization time. (This not a really nice solution but
                    # it works).
                    time.sleep(0.1)
                for device in new_devices:
                    self._register_new_device(device)
            except:
                pass
            # We don't want to burn the Pi :P.
            time.sleep(0.1)

        # When the manager was stopped, deregister all sensors.
        for device in manager.get_available_devices():
            self._deregister_device(device)

    def _deregister_device(self, device: str):
        """
        Will be called when a device lost connection.

        :param device: The device that lost connection.
        """

        # Will deregister the device.
        sensor_manager = SensorManager.get_instance()  # type: SensorManager
        sensor = sensor_manager.get_sensor_by_device(device)
        sensor_manager._deregister_sensor(sensor)

    def _register_new_device(self, device: str):
        """
        Will be called when a new device was found.

        :param device: The found device.
        """
        manager = service.serial.manager.Manager.get_instance()  # type: service.serial.manager.Manager

        # Create the serial connection with some listeners.
        on_exit = [_sensor_disconnect_listener]
        listeners = [_sensor_line_listener]
        try:
            manager.setup_connection(device, listeners, on_exit=on_exit)
        except:
            pass

        # Create a sensor for the serial connection.
        connection = manager.connections[device]  # type: SerialConnection

        sensor = Sensor(SensorType.UNKOWN, "unkown", device, connection)

        # Will register the sensor with the sensor manager.
        sensor_manager = SensorManager.get_instance()  # type: SensorManager
        sensor_manager._register_sensor(sensor)

        connection.send_command("ping", "", _update_information)


class SensorManager:
    """
    Will hold all connected sensors.
    """

    # Will store the singleton here.
    __instance = None

    @staticmethod
    def get_instance():
        """
        Will return the manager instance.

        :return: The manager instance.
        """
        if SensorManager.__instance is None:
            SensorManager()
        return SensorManager.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if SensorManager.__instance is not None:
            raise Exception("Only one instance of the manager should exist!")
        else:
            SensorManager.__instance = self
        self._sensors = {}  # type: Dict[str, Sensor]
        self._handler_watcher = []  # type: List[HandlerWatcher]

    def register_handler_watcher(self, handler_watcher: HandlerWatcher):
        """
        Will register a new handler watcher.

        :param handler_watcher: The handler watcher to register.
        """
        if handler_watcher not in self._handler_watcher:
            self._handler_watcher.append(handler_watcher)

    def get_sensor_devices(self) -> List[str]:
        """
        Will get all known sensor devices.

        :return: List of all known sensor devices.
        """
        return list(self._sensors.keys())

    def get_sensor_by_device(self, device: str) -> Sensor:
        """
        Will get a sensor by device id.

        :param device: Device id.
        :return: The sensor found at that device. When not found None is given.
        """
        sensor = None
        if device in self._sensors:
            sensor = self._sensors[device]
        return sensor

    def _trigger_type_handlers(self, device: str, line: str):
        """
        Will be called when a new line was received.

        :param device: The device id that triggered that did the triggering.
        :param line: The received line.
        """
        # Get the sensor and all handlers to be triggered.
        sensor = self._sensors[device]  # type: Sensor
        if not sensor.first_packet_received:
            self._trigger_first_first_packet_handler(sensor, line)

        handlers = self._trigger_type_handler_based_on_params(sensor.name,
                                                              sensor.sensor_type)

        # Trigger all handlers with line.
        for handler in handlers:
            handler.handle(sensor, line)

    def _trigger_first_first_packet_handler(self, sensor: Sensor, line: str):
        """
        Will be triggered when the sensor receives its first line and set the
        information of the sensor.

        :param sensor: The sensor that received its first line.
        :param line: Line that was received.
        """
        sensor.received_first_packet()
        contents = json.loads(line)
        # if name in contents:
        #     sensor._name = contents["name"]
        sensor._sensor_type = SensorType.from_string(contents["sensor"])

    def _trigger_type_handler_based_on_params(self, sensor_name: str,
                                              type: SensorType) -> List[
        AbstractHandler]:
        """
        Will return all handlers that should be called for given sensor.

        :param sensor_name: The name of the sensor to get the triggers of.
        :param type: The type of the sensor to get the triggers of.
        :return: Found handlers.
        """
        handlers = []
        for handler_factory in self._handler_watcher:
            for trigger in handler_factory.triggers:

                # If any fields match will trigger the handler.
                if trigger.any_field_match:
                    if sensor_name in trigger.sensor_names or type in trigger.sensor_types:
                        handlers.append(handler_factory.handler)

                # If all fields should match before the handlers can be triggered.
                elif sensor_name in trigger.sensor_names and type in trigger.sensor_types:
                    handlers.append(handler_factory.handler)
        return handlers

    def _register_sensor(self, sensor: Sensor):
        """
        Register a new sensor.

        :param sensor: Sensor to register.
        """
        self._sensors[sensor.device] = sensor

    def _deregister_sensor(self, sensor: Sensor):
        """
        Will deregister the sensor.

        :param sensor: The sensor to deregister.
        """

        # Remove connection and sensors.
        manager = service.serial.manager.Manager.get_instance()  # type: service.serial.manager.Manager
        manager.remove_connection(sensor.device)
        del self._sensors[sensor.device]

    def start(self):
        """
        Will start the manager and finding new sensors connected.
        """
        _SensorSearcher().start()

    def stop(self):
        """
        Will stop the manager.
        """
        _SensorSearcher._is_running = False

    @property
    def sensors(self) -> Dict[str, Sensor]:
        return self._sensors