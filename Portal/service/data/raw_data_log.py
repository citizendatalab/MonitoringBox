from typing import Dict, List


class RawDataLogManager:
    # Will store the singleton here.
    __instance = None

    MAX_LOG_ENTRIES = 100

    @staticmethod
    def get_instance():
        """
        Will return the manager instance.

        :return: The manager instance.
        """
        if RawDataLogManager.__instance is None:
            RawDataLogManager()
        return RawDataLogManager.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if RawDataLogManager.__instance is not None:
            raise Exception("Only one instance of the manager should exist!")
        else:
            RawDataLogManager.__instance = self

        self._log = {}  # type: Dict[str,List[str]]

    def log(self, device: str, line: str):
        if device not in self._log:
            self._log[device] = []
        if len(self._log[device]) == RawDataLogManager.MAX_LOG_ENTRIES:
            self._log[device].pop(len(self._log[device]) - 1)
        self._log[device].insert(0, line)

    def get_log(self, device: str) -> List[str]:
        if device not in self._log:
            return []
        return self._log[device]
