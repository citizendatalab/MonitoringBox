from service.sensor.handlers.abstract_handler import AbstractHandler


class HandlerWatcher:
    """
    Will give the triggers for a handler and the handler it self.
    """

    def __init__(self, triggers,
                 handler: AbstractHandler):
        self._triggers = triggers
        self._handler = handler

    @property
    def triggers(self):
        """
        :return: The triggers for this handler.
        """
        return self._triggers

    @property
    def handler(self) -> AbstractHandler:
        """
        :return: The handler that can be triggered.
        """
        return self._handler
