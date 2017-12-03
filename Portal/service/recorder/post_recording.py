import json
import os
import threading
from enum import Enum
from typing import List, Dict

from io import TextIOWrapper
import csv

import _csv
import zipfile
from service.recorder.recordings_manager import Recording
from service.sensor_manager import Sensor, SensorType


class ProgressInformer:
    def status_update(self, value: int, max: int) -> None:
        raise NotImplemented()


class FormatEnum(Enum):
    CSV = "CSV",
    RAW = "RAW"

    @staticmethod
    def from_string(input_str: str):
        out = None
        for format_type in FormatEnum:
            format_type = format_type  # type: FormatEnum
            if format_type.name == input_str:
                out = format_type
        if out is None:
            raise Exception("unkown type given")
        return out


# class FormatMakerThread(threading.Thread):
#     def __init__(self, recording: Recording, format: FormatEnum,
#                  progress_informer: ProgressInformer):
#         super(FormatMakerThread, self).__init__()
#         self._progress_informer = progress_informer
#         self._format = format
#         self._recording = recording
#
#     def run(self):
#         for i in range(0, 100):
#             self._progress_informer.status_update(i, 100)

class AbstractFormatConverter:
    def get_export_folder(self, recording: Recording) -> str:
        export_folder = os.path.join(recording.path, "exports")
        if not os.path.exists(export_folder):
            os.mkdir(export_folder)
        return export_folder

        def create_format(self, recording: Recording,
                          progress_informer: ProgressInformer) -> str:
            raise NotImplemented()


class AbstractSensorWriter:
    def get_headers(self) -> List[str]:
        return []

    def get_values(self, record: str):
        return record


class ExampleSensorWriter(AbstractSensorWriter):
    def get_headers(self):
        return ["count"]

    def get_values(self, record: str):
        a = json.loads(record)
        count = a["data"]["data"]["count"]
        return [count]


class HumidityTemperatureSensorWriter(AbstractSensorWriter):
    def get_headers(self):
        return ["Temperature", "Humidity"]

    def get_values(self, record: str):
        a = json.loads(record)
        data = a["data"]["data"]
        return [data["Temperature"], data["Humidity"]]


class CO2SensorWriter(AbstractSensorWriter):
    def get_headers(self):
        return ["CO2 value"]

    def get_values(self, record: str):
        temp = json.loads(record)
        data = temp["data"]["data"]
        return [data["Value"]]


class HeartRateSensorWriter(AbstractSensorWriter):
    def get_headers(self):
        return ["Heart rate - ir value", "Heart rate - bpm"]

    def get_values(self, record: str):
        a = json.loads(record)
        data = a["data"]["data"]
        return [data["irValue"], data["beatsPerMinute"]]


class PiCamWriter(AbstractSensorWriter):
    def get_headers(self):
        return ["Pi cam - picture", "Pi cam - date", "Pi cam - time"]

    def get_values(self, record: str):
        data = json.loads(record)
        data = data["data"]
        return [data["location"], data["date"], data["time"]]


def get_sensor_writer(sensor: Sensor):
    if sensor.sensor_type == SensorType.EXAMPLE_SENSOR:
        return ExampleSensorWriter()
    elif sensor.sensor_type == SensorType.HUMIDITY_TEMPERATURE_SENSOR:
        return HumidityTemperatureSensorWriter()
    elif sensor.sensor_type == SensorType.CO2_SENSOR:
        return CO2SensorWriter()
    elif sensor.sensor_type == SensorType.HEART_RATE_SENSOR:
        return HeartRateSensorWriter()
    elif sensor.sensor_type == SensorType.PI_CAMERA:
        return PiCamWriter()
    raise NotImplemented()


class CSVFormatConverter(AbstractFormatConverter):
    def _write_header(self, recording: Recording, writer: _csv.writer):
        columns = []
        for sensor in recording.record_details.sensor_details:
            for sensor in get_sensor_writer(sensor).get_headers():
                columns.append(sensor)
        writer.writerow(columns)

    def create_format(self, recording: Recording,
                      progress_informer: ProgressInformer) -> str:
        folder = os.path.join(self.get_export_folder(recording), "CSV")
        if not os.path.exists(folder):
            os.mkdir(folder)
        path = os.path.join(folder, "csv.csv")
        if os.path.exists(path):
            return path

        with open(path, "w") as file:
            writer = csv.writer(file)
            self._write_header(recording, writer)
            handlers = self._get_sensor_file_handlers(recording)
            self._write_sensor_data(writer, handlers, recording)

        return path

    def _get_sensor_file_handler_key(self, sensor: Sensor) -> str:
        return sensor.sensor_type.name + "-" + sensor.device

    def _get_sensor_file_handlers(self, recording: Recording) -> Dict[
        str, TextIOWrapper]:
        file_handlers = {}
        for sensor in recording.record_details.sensor_details:
            path = os.path.join(recording.path, sensor.sensor_type.name,
                                sensor.device.replace("/", "_") + ".dat")
            file_handlers[self._get_sensor_file_handler_key(sensor)] = open(
                path, "r")
        return file_handlers

    def _write_sensor_data(self, writer: _csv.writer,
                           handlers: Dict[str, TextIOWrapper],
                           recording: Recording):
        working = True
        has_data = {}
        for sensor in recording.record_details.sensor_details:
            has_data[self._get_sensor_file_handler_key(sensor)] = True
        current_cycle = 0
        while working:
            columns = []
            for sensor in recording.record_details.sensor_details:
                handler = handlers[self._get_sensor_file_handler_key(sensor)]
                sensor_writer = get_sensor_writer(sensor)
                values = [""] * len(sensor_writer.get_headers())
                line = handler.readline()
                has_data[
                    self._get_sensor_file_handler_key(sensor)] = line != ""
                if has_data[self._get_sensor_file_handler_key(
                        sensor)] and current_cycle == self._get_cycle(line):
                    values = sensor_writer.get_values(line)

                for value in values:
                    columns.append(value)

            writer.writerow(columns)
            working = False
            for item in has_data:
                if has_data[item]:
                    working = True
                    break
            current_cycle += 1

    def _get_cycle(self, line: str) -> int:
        return json.loads(line)["cycle"]


class RAWFormatConverter(AbstractFormatConverter):
    def _get_sensor_paths(self, recording: Recording, sensor: Sensor) -> str:
        out = [os.path.join(recording.path, sensor.sensor_type.name,
                            sensor.device.replace("/", "_")) + ".dat"]

        if sensor.sensor_type == SensorType.PI_CAMERA:
            path = os.path.join(recording.path, sensor.sensor_type.name)
            items = os.listdir(path)
            for name in items:
                out.append(os.path.join(path, name))
        return out

    def _archive_get_sensor_paths(self, sensor: Sensor) -> str:
        out = [os.path.join(sensor.sensor_type.name,
                            sensor.device.replace("/", "_")) + ".dat"]
        if sensor.sensor_type == SensorType.PI_CAMERA:
            path = os.path.join(sensor.sensor_type.name)
            items = os.listdir(path)
            for name in items:
                out.append(os.path.join(path, name))
        return out

    def create_format(self, recording: Recording,
                      progress_informer: ProgressInformer) -> str:

        folder = os.path.join(self.get_export_folder(recording), "RAW")
        if not os.path.exists(folder):
            os.mkdir(folder)
        path = os.path.join(folder, "raw.zip")
        if os.path.exists(path):
            return path

        zf = zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED)

        for sensor in recording.record_details.sensor_details:
            file_paths = self._get_sensor_paths(recording, sensor)
            archive_paths = self._archive_get_sensor_paths(sensor)
            i = 0
            for file_path in file_paths:
                archive_path = archive_paths[i]
                zf.write(file_path, archive_path)
                i += 1
        zf.close()
        return path


class FormatMaker:
    _format_converters = {
        FormatEnum.CSV: CSVFormatConverter(),
        FormatEnum.RAW: RAWFormatConverter()  # @todo implement this
    }

    def _get_format_converter(self,
                              format: FormatEnum) -> AbstractFormatConverter:
        return self._format_converters[format]

    def create_format(self, recording: Recording, format: FormatEnum,
                      progress_informer: ProgressInformer) -> str:
        converter = self._get_format_converter(format)
        return converter.create_format(recording, progress_informer)
