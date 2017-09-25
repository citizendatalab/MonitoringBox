import service.serial.manager
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify

import service.sensor_manager
import service.sensor.handler_factory
from service.sensor.handler_factory import HandlerFactory
from service.sensor_manager import HandlerTrigger
from service.sensor_manager import SensorType
from service.sensor.handlers.simple_handler import SimpleHandler

current = 0

# manager = service.serial.manager.Manager.get_instance()  # type: service.serial.manager.Manager
sensor_manager = service.sensor_manager.SensorManager.get_instance()  # type:service.sensor_manager.SensorManager
sensor_manager.start()

sensor_manager.register_handler_factory(
    HandlerFactory([
        HandlerTrigger([
            SensorType.UNKOWN
        ], [], True),
    ], SimpleHandler())
)


def test(connection, a):
    global current
    current = a
    print(a)


# manager.setup_connection('/dev/ttyUSB0', [test])
app = Flask(__name__)  # create the application instance :)


@app.route('/')
def show_entries():
    global current
    for device in service.serial.manager.Manager.get_available_devices():
        print(device)
    return render_template('show_entries.html', current=current)


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')

# pip install Flask
# pip install pyserial
