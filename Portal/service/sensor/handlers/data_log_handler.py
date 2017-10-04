from service.sensor.handlers.abstract_handler import AbstractHandler
from service.sensor_manager import Sensor
from service.data.raw_data_log import RawDataLogManager


class DataLogHandler(AbstractHandler):
    """
    Example handler, will just print the received line.
    """

    def handle(self, sensor: Sensor, line: str):
        manager = RawDataLogManager.get_instance()  # type: RawDataLogManager
        manager.log(sensor.device, line)
