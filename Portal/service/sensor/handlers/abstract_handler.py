from abc import ABC


class AbstractHandler(ABC):
    def handle(self, line: str):
        """
        Will handle received line.

        :param line: The recieved line.
        """
        raise NotImplemented("handle was not implemented for class")
