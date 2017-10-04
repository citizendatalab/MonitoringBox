from abc import ABC


class AbstractHandler(ABC):
    def handle(self, triggeredBy, line: str):
        """
        Will handle received line.

        :param triggeredBy: The sensor where the data originated from.
        :param line: The recieved line.
        """
        raise NotImplemented("handle was not implemented for class")
