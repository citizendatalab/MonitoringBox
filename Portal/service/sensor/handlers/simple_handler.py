from service.sensor.handlers.abstract_handler import AbstractHandler


class SimpleHandler(AbstractHandler):
    def handle(self, line: str):
        print(line)
