from enum import Enum
from typing import List, Callable
import threading
import service.serial.manager
import time
from service.sensor.handler_factory import HandlerFactory
from service.sensor.handlers.abstract_handler import AbstractHandler


class SensorType(Enum):
    UNKOWN = -2
    EXAMPLE_SENSOR = -1
    PI_CAMERA = 0
    GPS_SENSOR = 1
    HUMIDITY_TEMPERATURE_SENSOR = 2
    CO2_SENSOR = 3
    HEART_RATE_SENSOR = 4
    GALVANIC_SKIN_RESPONSE_SENSOR = 5


class HandlerTrigger:
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
        return self._sensor_types

    @property
    def sensor_names(self) -> List[str]:
        return self._sensor_names


class Sensor:
    def __init__(self, type: SensorType, name: str, device: str,
                 connection: service.serial.manager.SerialConnection):
        self._connection = connection
        self._device = device
        self._type = type
        self._name = name

    @property
    def connection(self):
        return self._connection

    @property
    def device(self):
        return self._device

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name


def _sensor_disconnect_listener(
        connection: service.serial.manager.SerialConnection):
    sensor_manager = SensorManager.get_instance()  # type: SensorManager
    sensor = sensor_manager.get_sensor_by_device(
        connection.device)  # type: Sensor
    sensor_manager._deregister_sensor(sensor)


def _sensor_line_listener(
        connection: service.serial.manager.SerialConnection, line: str):
    manager = SensorManager.get_instance()  # type: SensorManager
    manager._trigger_type_handlers(connection.device, line)


class _SensorSearcher(threading.Thread):
    _is_running = False

    def run(self):
        _SensorSearcher._is_running = True
        manager = service.serial.manager.Manager.get_instance()  # type: Manager
        sensor_manager = SensorManager.get_instance()  # type: SensorManager
        while _SensorSearcher._is_running:
            try:
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
                                                              sensor.type)
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
