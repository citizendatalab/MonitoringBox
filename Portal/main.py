import service.serial.manager
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify

import service.sensor_manager
import service.sensor.handler_factory
from service.sensor.handler_factory import HandlerFactory
from service.sensor_manager import HandlerTrigger
from service.sensor_manager import SensorType
from service.sensor.handlers.simple_handler import SimpleHandler
import datetime
import service.helper.table as table

current = 0
sensor_manager = service.sensor_manager.SensorManager.get_instance()  # type:service.sensor_manager.SensorManager
sensor_manager.start()

# Register all handlers for sensors.
sensor_manager.register_handler_factory(
    HandlerFactory([
        HandlerTrigger([
            SensorType.UNKOWN
        ], [], True),
    ], SimpleHandler())
)

app = Flask(__name__)  # create the application instance :)


# Route handlers

@app.route('/')
@app.route('/connected_sensors')
def show_entries():
    global current
    return render_template('connected_sensors.html', current=current)


@app.route('/recordings')
def show_recordings():
    global current
    return render_template('recordings.html', current=current)


@app.route('/settings')
def show_settings():
    global current
    return render_template('settings.html', current=current)


@app.route('/device_options')
def show_device_options():
    global current
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


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

    # pip install Flask
    # pip install pyserial
