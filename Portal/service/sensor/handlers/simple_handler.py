from service.sensor.handlers.abstract_handler import AbstractHandler
from service.sensor_manager import Sensor


class SimpleHandler(AbstractHandler):
    """
    Example handler, will just print the received line.
    """

    def handle(self, sensor: Sensor, line: str):
        print(line)
