import service.serial.manager
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify

import service.sensor_manager
import service.sensor.handler_watcher
from service.sensor.handler_watcher import HandlerWatcher
from service.sensor_manager import HandlerTrigger
from service.sensor_manager import SensorType
from service.sensor.handlers.data_log_handler import DataLogHandler
from service.sensor.handlers.simple_handler import SimpleHandler
import datetime
import service.helper.table as table
import service.data.disk
import service.data.connection
import base64
from urllib.parse import quote
from service.data.raw_data_log import RawDataLogManager
from PyQt4 import QtGui, QtCore
import math
import threading
from service.sensor_manager import Sensor
import time
import picamera

camera = picamera.PiCamera()
camera.resolution = (1024, 768)
camera.start_preview()

current = 0
sensor_manager = service.sensor_manager.SensorManager.get_instance()  # type:service.sensor_manager.SensorManager
sensor_manager.start()

# Register all handlers for sensors.
sensor_manager.register_handler_watcher(
    HandlerWatcher([
        HandlerTrigger([
            SensorType.UNKOWN,
        ], [], True),
    ], SimpleHandler())
)
sensor_manager.register_handler_watcher(
    HandlerWatcher([
        HandlerTrigger([
            SensorType.UNKOWN,
            SensorType.CO2_SENSOR,
            SensorType.EXAMPLE_SENSOR,
            SensorType.GALVANIC_SKIN_RESPONSE_SENSOR,
            SensorType.GPS_SENSOR,
            SensorType.HEART_RATE_SENSOR,
            SensorType.HUMIDITY_TEMPERATURE_SENSOR
        ], [], True),
    ], DataLogHandler())
)

app = Flask(__name__)  # create the application instance :)


def get_sensor_icon(sensor: Sensor) -> str:
    types = {
        SensorType.UNKOWN: "<i class=\"fa fa-question\" aria-hidden=\"true\"></i>",
        SensorType.CO2_SENSOR: "<i class=\"fa fa-question\" aria-hidden=\"true\"></i>",
        SensorType.EXAMPLE_SENSOR: "<i class=\"fa fa-cogs\" aria-hidden=\"true\"></i>",
        SensorType.GALVANIC_SKIN_RESPONSE_SENSOR: "<i class=\"fa fa-question\" aria-hidden=\"true\"></i>",
        SensorType.GPS_SENSOR: "<i class=\"fa fa-question\" aria-hidden=\"true\"></i>",
        SensorType.HEART_RATE_SENSOR: "<i class=\"fa fa-question\" aria-hidden=\"true\"></i>",
        SensorType.HUMIDITY_TEMPERATURE_SENSOR: "<i class=\"fa fa-question\" aria-hidden=\"true\"></i>"
    }
    if sensor.sensor_type in types:
        return types[sensor.sensor_type]
    else:
        return types[SensorType.SensorType.UNKOWN]


# Route handlers

@app.route('/')
@app.route('/connected_sensors')
def show_entries():
    return render_template('connected_sensors.html', current=current)


@app.route('/recordings')
def show_recordings():
    return render_template('recordings.html', current=current)


@app.route('/camera')
def show_camera():
    camera.capture('image.png')
    image = open('image.png', 'rb')
    image_read = image.read()
    image_64_encode = base64.encodestring(image_read)
    return render_template('camera.html', image_64_encode=image_64_encode.decode("UTF-8"))


@app.route('/device/<device>/raw_data')
def show_device_raw_data(device):
    device_id = base64.b64decode(device).decode("UTF-8")
    sensor_manager = service.sensor_manager.SensorManager.get_instance()  # type:service.sensor_manager.SensorManager
    sensor = sensor_manager.get_sensor_by_device(device_id)
    if sensor is None:
        abort(404)
    else:
        return render_template('raw_data.html', sensor=sensor, device=device,
                               device_id=device_id)


def human_readable_size(size):
    n = math.floor(math.log(size, 1024))
    size_names = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    return str(round(size / math.pow(1024, n), 1)) + size_names[n + 1]


@app.route('/settings', methods=['GET', 'POST'])
def show_settings():
    if request.method == 'POST':
        recording_format = request.form["recording_format"]
        recording_location = request.form["recording_location"]
        connection = service.data.connection.Connection.get_instance()
        connection.put_setting("recording.format", recording_format)
        connection.put_setting("recording.location", recording_location)

    config = service.data.connection.Connection.get_instance()  # type: service.data.connection.Connection

    settings = {"options": {}, "current": {}}
    settings["options"]["mounts"] = []
    for mount in service.data.disk.get_mounts():
        if mount.mount_point not in ["/bin", "/dev", "/etc", "/lib", "/boot",
                                     "/home", "/mnt", "/proc", "/tmp", "/usr",
                                     "/var", "/sbin", "/kernel"]:
            mount = mount.get_dict()
            mount["percent_usage"] = round(mount["percent_usage"], 2)
            mount["free_space_human_readable"] = human_readable_size(
                mount["size"] - mount["used"])
            settings["options"]["mounts"].append(mount)

    settings["current"]["selected_mount"] = config.get_setting(
        "recording.location", "/")

    return render_template('settings.html', settings=settings)


@app.route('/device_options')
def show_device_options():
    return render_template('device_options.html', current=current)


@app.route('/api/test')
def test():
    results_per_page = int(request.args.get('per_page', 10))
    results_start = int(request.args.get('start', 0))

    resp_table = table.generate_table(200, results_per_page, results_start,
                                      ["a", "b", "c"])

    for i in range(results_start, results_start + results_per_page):
        resp_table.table_body.append(
            ["hoi" + str(i), "test", "dinges" + str(datetime.datetime.now())])
    return jsonify(resp_table.as_dict())

import io
@app.route('/api/camera/picture')
def show_api_camera():
    # camera.capture('image.png')
    # image = open('image.png', 'rb')
    # image_read = image.read()
    # image_64_encode = base64.encodestring(image_read)
    # Create an in-memory stream
    my_stream = io.BytesIO()
    with picamera.PiCamera() as camera:
        # Camera warm-up time
        camera.capture(my_stream, 'jpeg')

    image_64_encode = base64.b64encode(my_stream.getvalue())
    amount = 1
    resp_table = table.generate_table(amount, amount,
                                      0,
                                      [""], [amount], 1)
    resp_table.show_heading = False

    # <img src="data:image/png;base64,{{image_64_encode}}"/>
    resp_table.table_body.append(["<img src=\"data:image/png;base64," + image_64_encode.decode("UTF-8") + "\"/>"])
    return jsonify(resp_table.as_dict())

    # return render_template('camera.html', image_64_encode=image_64_encode.decode("UTF-8"))

@app.route('/api/sensors/list')
def show_api_sensors_list():
    results_per_page = int(request.args.get('per_page', 10))
    results_start = int(request.args.get('start', 0))

    sensor_manager = service.sensor_manager.SensorManager.get_instance()  # type:service.sensor_manager.SensorManager
    devices = sensor_manager.get_sensor_devices()

    resp_table = table.generate_table(len(devices), results_per_page,
                                      results_start,
                                      ["Name", "Sensor type", "Port", ""])

    for device in devices[results_start: results_start + results_per_page]:
        sensor = sensor_manager.get_sensor_by_device(device)

        device_id = base64.b64encode(bytes(device, "UTF-8"))
        resp_table.table_body.append(
            [sensor.name,
             get_sensor_icon(sensor) + " " + sensor.sensor_type.name,
             device,
             "<a href=\"device/" + quote(
                 device_id) + "/raw_data\">Raw data</a>"])
    return jsonify(resp_table.as_dict())


@app.route('/api/device/<device>/raw_data')
def api_device_raw_data(device):
    device_id = base64.b64decode(device).decode("UTF-8")
    sensor_manager = service.sensor_manager.SensorManager.get_instance()  # type:service.sensor_manager.SensorManager
    sensor = sensor_manager.get_sensor_by_device(device_id)

    amount = 20

    manager = RawDataLogManager.get_instance()  # type: RawDataLogManager

    log = manager.get_log(device_id)
    resp_table = table.generate_table(amount, amount,
                                      0,
                                      [""], [amount], 1)
    resp_table.show_heading = False

    for k in log[0:(amount - 1)]:
        resp_table.table_body.append([k])
    return jsonify(resp_table.as_dict())


class Example(QtGui.QWidget):
    def __init__(self):
        super(Example, self).__init__()

        self.initUI()
        self.frame = 0

    def initUI(self):
        self.setGeometry(500, 500, 500, 500)
        self.setWindowTitle('Pen styles')
        self.show()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawLines(qp)
        qp.end()
        self.frame += 1

    def drawLines(self, qp):
        pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        slowdown = 20
        size = 75 + (math.sin(self.frame / slowdown) * 50)
        qp.drawLine(250 + (math.sin(self.frame / slowdown) * size),
                    150 + ((math.cos(self.frame / slowdown) * size) * 0.5),
                    250 + (
                        math.sin(
                            (self.frame / slowdown) + (math.pi / 2)) * size),
                    150 + ((math.cos(
                        (self.frame / slowdown) + (math.pi / 2)) * size)) * 0.5)

        qp.drawLine(
            250 + (math.sin((self.frame / slowdown) + (math.pi / 2)) * size),
            150 + (
                (math.cos(
                    (self.frame / slowdown) + (math.pi / 2)) * size) * 0.5),
            250 + (math.sin((self.frame / slowdown) + math.pi) * size),
            150 + ((math.cos((self.frame / slowdown) + math.pi) * size) * 0.5)
        )

        qp.drawLine(
            250 + (math.sin((self.frame / slowdown) - (math.pi / 2)) * size),
            150 + (
                (math.cos(
                    (self.frame / slowdown) - (math.pi / 2)) * size) * 0.5),
            250 + (math.sin((self.frame / slowdown) + math.pi) * size),
            150 + ((math.cos((self.frame / slowdown) + math.pi) * size) * 0.5)
        )

        qp.drawLine(
            250 + (math.sin((self.frame / slowdown) - (math.pi / 2)) * size),
            150 + (
                (math.cos(
                    (self.frame / slowdown) - (math.pi / 2)) * size) * 0.5),
            250 + (math.sin((self.frame / slowdown) + (math.pi * 2)) * size),
            150 + (
                (math.cos(
                    (self.frame / slowdown) + (math.pi * 2)) * size) * 0.5))

        qp.drawLine(250 + (math.sin(self.frame / slowdown) * size),
                    250 + ((math.cos(self.frame / slowdown) * size) * 0.5),
                    250 + (
                        math.sin(
                            (self.frame / slowdown) + (math.pi / 2)) * size),
                    250 + (
                        (math.cos(
                            (self.frame / slowdown) + (
                                math.pi / 2)) * size)) * 0.5)

        qp.drawLine(
            250 + (math.sin((self.frame / slowdown) + (math.pi / 2)) * size),
            250 + (
                (math.cos(
                    (self.frame / slowdown) + (math.pi / 2)) * size) * 0.5),
            250 + (math.sin((self.frame / slowdown) + math.pi) * size),
            250 + ((math.cos((self.frame / slowdown) + math.pi) * size) * 0.5)
        )

        qp.drawLine(
            250 + (math.sin((self.frame / slowdown) - (math.pi / 2)) * size),
            250 + (
                (math.cos(
                    (self.frame / slowdown) - (math.pi / 2)) * size) * 0.5),
            250 + (math.sin((self.frame / slowdown) + math.pi) * size),
            250 + ((math.cos((self.frame / slowdown) + math.pi) * size) * 0.5)
        )

        qp.drawLine(
            250 + (math.sin((self.frame / slowdown) - (math.pi / 2)) * size),
            250 + (
                (math.cos(
                    (self.frame / slowdown) - (math.pi / 2)) * size) * 0.5),
            250 + (math.sin((self.frame / slowdown) + (math.pi * 2)) * size),
            250 + (
                (math.cos(
                    (self.frame / slowdown) + (math.pi * 2)) * size) * 0.5))

        qp.drawLine(
            250 + (math.sin((self.frame / slowdown) + (math.pi / 2)) * size),
            150 + (
                (math.cos(
                    (self.frame / slowdown) + (math.pi / 2)) * size) * 0.5),
            250 + (math.sin((self.frame / slowdown) + (math.pi / 2)) * size),
            250 + (
                (math.cos(
                    (self.frame / slowdown) + (math.pi / 2)) * size)) * 0.5)

        qp.drawLine(250 + (math.sin((self.frame / slowdown) + math.pi) * size),
                    150 + (
                        (math.cos(
                            (self.frame / slowdown) + math.pi) * size) * 0.5),
                    250 + (math.sin((self.frame / slowdown) + math.pi) * size),
                    250 + (
                        (math.cos(
                            (self.frame / slowdown) + math.pi) * size) * 0.5)
                    )

        qp.drawLine(
            250 + (math.sin((self.frame / slowdown) - (math.pi / 2)) * size),
            150 + (
                (math.cos(
                    (self.frame / slowdown) - (math.pi / 2)) * size) * 0.5),
            250 + (math.sin((self.frame / slowdown) - (math.pi / 2)) * size),
            250 + (
                (
                    math.cos(
                        (self.frame / slowdown) - (math.pi / 2)) * size) * 0.5)
        )

        qp.drawLine(
            250 + (math.sin((self.frame / slowdown) + (math.pi * 2)) * size),
            150 + (
                (math.cos(
                    (self.frame / slowdown) + (math.pi * 2)) * size) * 0.5),
            250 + (math.sin((self.frame / slowdown) + (math.pi * 2)) * size),
            250 + (
                (math.cos(
                    (self.frame / slowdown) + (math.pi * 2)) * size) * 0.5))


# class Refresher(threading.Thread):
#     def run(self):
#

class App(threading.Thread):
    def run(self):
        app.run(debug=False, host='0.0.0.0')


if __name__ == "__main__":
    App().start()
    # Refresher().start()
    # mainWindow= QtGui.QApplication(sys.argv)
    # ex = Example()
    #
    # # width = mainWindow.frameGeometry().width()
    # # height = mainWindow.frameGeometry().height()
    # # ex.resize(width,height)
    # a = True
    # while True:
    #     ex.repaint()
    #     time.sleep((1/3)/10)
    # sys.exit(mainWindow.exec_())

# modules that should be installed.
# pip install Flask
# pip install pyserial
