from service.sensor.handlers.abstract_handler import AbstractHandler


class SimpleHandler(AbstractHandler):
    """
    Example handler, will just print the received line.
    """

    def handle(self, line: str):
        print(line)
