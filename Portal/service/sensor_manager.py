from enum import Enum
from typing import List, Callable
import threading
import service.serial.manager
import time
from service.sensor.handler_factory import HandlerFactory
from service.sensor.handlers.abstract_handler import AbstractHandler


class SensorType(Enum):
    """
    Defines a sensor type.
    """
    UNKOWN = -2
    EXAMPLE_SENSOR = -1
    PI_CAMERA = 0
    GPS_SENSOR = 1
    HUMIDITY_TEMPERATURE_SENSOR = 2
    CO2_SENSOR = 3
    HEART_RATE_SENSOR = 4
    GALVANIC_SKIN_RESPONSE_SENSOR = 5


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

    @property
    def name(self):
        """
        :return: The name of the sensor.
        """
        return self._name


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
                    self._deregister_device(device)
                for device in new_devices:
                    self._register_new_device(device)
            except:
                pass
            # We don't want to burn the Pi :P.
            time.sleep(0.1)

    def _handle_found_devices(self, found_devices: List[str]):
        for device in found_devices:
            manager = SensorManager.get_instance()  # type: SensorManager
            if manager.get_sensor_by_device(device) is None:
                self._register_new_device(device)

    def _deregister_device(self, device: str):
        sensor_manager = SensorManager.get_instance()  # type: SensorManager
        sensor = sensor_manager.get_sensor_by_device(device)
        sensor_manager._deregister_sensor(sensor)

    def _register_new_device(self, device: str):
        manager = service.serial.manager.Manager.get_instance()  # type: service.serial.manager.Manager
        on_exit = [_sensor_disconnect_listener]
        listeners = [_sensor_line_listener]
        manager.setup_connection(device, listeners, on_exit=on_exit)

        connection = manager.connections[device]
        sensor = Sensor(SensorType.UNKOWN, "", device, connection)

        sensor_manager = SensorManager.get_instance()  # type: SensorManager
        sensor_manager._register_sensor(sensor)


class SensorManager:
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
        self._sensors = {}
        self._handler_factories = []  # type: List[HandlerFactory]

    def register_handler_factory(self, handler_factory: HandlerFactory):
        if handler_factory not in self._handler_factories:
            self._handler_factories.append(handler_factory)

    def get_sensor_devices(self):
        return list(self._sensors.keys())

    def get_sensor_by_device(self, device: str):
        sensor = None
        if device in self._sensors:
            sensor = self._sensors[device]
        return sensor

    def _trigger_type_handlers(self, device: str, line: str):
        sensor = self._sensors[device]  # type: Sensor
        handlers = self._trigger_type_handler_based_on_params(sensor.name,
                                                              sensor.sensor_type)
        for handler in handlers:
            handler.handle(line)

    def _trigger_type_handler_based_on_params(self, sensor_name: str,
                                              type: SensorType) -> List[
        AbstractHandler]:
        handlers = []
        for handler_factory in self._handler_factories:
            for trigger in handler_factory.triggers:
                if trigger.any_field_match:
                    if sensor_name in trigger.sensor_names or type in trigger.sensor_types:
                        handlers.append(handler_factory.handler)
                    elif sensor_name in trigger.sensor_names and type in trigger.sensor_types:
                        handlers.append(handler_factory.handler)
        return handlers

    def _register_sensor(self, sensor: Sensor):
        self._sensors[sensor.device] = sensor

    def _deregister_sensor(self, sensor: Sensor):
        manager = service.serial.manager.Manager.get_instance()  # type: service.serial.manager.Manager
        manager.remove_connection(sensor.device)
        del self._sensors[sensor.device]

    def start(self):
        _SensorSearcher().start()

    def stop(self):
        _SensorSearcher._is_running = False
