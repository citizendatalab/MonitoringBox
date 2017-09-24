# all the imports
import os
import serial
import time
# import sqlite3

from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify


# with serial.Serial('/dev/ttyUSB0', 9600, timeout=1) as ser:
#     a = ser  # type: serial.Serial
#     i = 10
#     while i > 0:
#         line = ser.readline()  # read a '\n' terminated line
#         print(line.decode("utf-8"))
#         time.sleep(0.25)
#         i -= 1
#     ser.close()

app = Flask(__name__)  # create the application instance :)

@app.route('/')
def show_entries():
    # db = get_db()
    # cur = db.execute('select title, text from entries order by id desc')
    # entries = cur.fetchall()
    return render_template('show_entries.html')


if __name__ == "__main__":
    app.run(debug=True)

# pip install Flask
# pip install pyserial
