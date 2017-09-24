from typing import Dict

import serial
import serial.threaded

import threading


class SerialConnection(threading.Thread):
    def __init__(self, listeners, device, baudrate):
        threading.Thread.__init__(self)
        self.baudrate = baudrate
        self.device = device
        self.listeners = listeners

    def run(self):
        with serial.Serial(self.device, self.baudrate, timeout=1) as ser:
            while True:
                line = ser.readline()  # read a '\n' terminated line
                self._call_listeners(line.decode("utf-8"))
            ser.close()

    def _call_listeners(self, line):
        for listener in self.listeners:
            listener(line)


class Manager:
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if Manager.__instance == None:
            Manager()
        return Manager.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Manager.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Manager.__instance = self
        self._connections = {}  # type: Dict[str,SerialConnection]

    def setupConnection(self, device: str, listeners=[], baudrate=9600):
        if device in self._connections:
            raise Exception("Connection already exists")
        self._connections[device] = SerialConnection(listeners, device,
                                                     baudrate)
        self._connections[device].start()

    def get_listeners(self, device):
        return self._connections[device].listeners
