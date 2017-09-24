# all the imports
import os
from typing import Dict, List, Callable
import serial
import serial.threaded
import service.serial.manager
import sys
import time

from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify


current = 0
manager = service.serial.manager.Manager.getInstance()  # type: service.serial.manager.Manager
def test(a):
    global current
    current = a
    print("a" + a)


def test2(a):
    print("a2" + a)


manager.setupConnection('/dev/ttyUSB0', [test])
# manager.get_listeners('/dev/ttyUSB0').append(test2)
app = Flask(__name__)  # create the application instance :)

@app.route('/')
def show_entries():
    # db = get_db()
    # cur = db.execute('select title, text from entries order by id desc')
    # entries = cur.fetchall()
    global current
    return render_template('show_entries.html', current=current)


if __name__ == "__main__":
    app.run(debug=True)

# pip install Flask
# pip install pyserial
