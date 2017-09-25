from service.sensor.handlers.abstract_handler import AbstractHandler


class HandlerFactory:
    def __init__(self, triggers,
                 handler: AbstractHandler):
        self._triggers = triggers
        self._handler = handler

    @property
    def triggers(self):
        return self._triggers

    @property
    def handler(self) -> AbstractHandler:
        return self._handler
