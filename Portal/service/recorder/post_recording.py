import threading
from enum import Enum

from service.recorder.recordings_manager import Recording


class ProgressInformer:
    def status_update(self, value: int, max: int) -> None:
        raise NotImplemented()


class FormatEnum(Enum):
    CSV = "CSV",


class FormatMakerThread(threading.Thread):
    def __init__(self, recording: Recording, format: FormatEnum,
                 progress_informer: ProgressInformer):
        super(FormatMakerThread, self).__init__()
        self._progress_informer = progress_informer
        self._format = format
        self._recording = recording

    def run(self):
        for i in range(0, 100):
            self._progress_informer.status_update(i, 100)


class FormatMaker:
    def create_format(self, recording: Recording, format: FormatEnum,
                      progress_informer: ProgressInformer):
        pass
