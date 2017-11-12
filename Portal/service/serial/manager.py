from queue import Queue
from typing import Dict, List, Callable
import serial
import serial.threaded
import threading
import serial.tools.list_ports
import time
import json

import io


class SerialConnection(threading.Thread):
    """
    Will hold a serial connection and inform the listeners when data arrives.
    """

    def __init__(self, listeners: List[Callable], device: str, baudrate: int,
                 on_exit: List[Callable]):
        threading.Thread.__init__(self)
        self.on_exit = on_exit  # type: List[Callable]
        self.baudrate = baudrate  # type: int
        self.device = device  # type: str
        self.listeners = listeners  # type: List[Callable]
        self._lock = threading.Lock()  # type: threading.Lock
        self._command_queue = Queue()

    def get_command(self):
        if not self._lock.acquire(False):
            return None
        command = None
        if not self._command_queue.empty():
            command = self._command_queue.get()
        self._lock.release()

        return command

    def handle_command_sending(self, connection: serial.Serial):
        command = self.get_command()
        if command:
            connection.write((command["command"] + ":" +
                             command["options"]).encode())
        return command

    def run(self):
        try:
            with serial.Serial(self.device, self.baudrate,
                               timeout=1) as connection:
                connection = connection  # type: serial.Serial

                # Give it one second of initialization time.
                time.sleep(1)
                try:

                    connection.flushInput()
                    connection.flushOutput()
                    # Keep looping until time the end of the universe.
                    while True:
                        command = self.handle_command_sending(connection)

                        # If there is no data in the buffer, wait.
                        while connection.inWaiting() == 0:
                            if command is None:
                                command = self.handle_command_sending(connection)
                            time.sleep(0.00000001)

                        # Read data until '\n' was reached.
                        line = connection.readline()  # type: bytes
                        #
                        # # When receiving data from the Arduino sometimes some
                        # # noise is sended so we need to filter that out.
                        # # 0x7B = '{' in the ASCII table.
                        while len(line) > 0 and line[0] != 0x7B:
                            line = line[1:]

                        # Call the listeners with the received string, when
                        # there is something to report.
                        if len(line) > 0:
                            self._call_listeners(
                                line.decode("utf-8").replace("'", "\""))
                        command["callback"](json.loads(line.decode("utf-8").replace("'", "\"")), self, command["callback_options"])

                except Exception as ex:
                    connection.close()

        except:
            # When the loop crashed for some reason (device is not connected
            # anymore) close the connection.
            self._call_exit_listeners()

    def _call_exit_listeners(self):
        """
        Will call all exit listeners.
        """
        for listener in self.on_exit:
            listener(self)

    def _call_listeners(self, line: str):
        """
        Will call all registered listeners, with line.

        :param line: Received line.
        """
        for listener in self.listeners:
            try:
                listener(self, line)
            except:
                pass

    def send_command(self, command: str, options=None, callback=None, callback_options=None):
        # Will lock the object.
        self._lock.acquire()
        self._command_queue.put({
            "command": command,
            "options": options,
            "callback": callback,
            "callback_options": callback_options
        })
        # Will make the object available again.
        self._lock.release()


class Manager:
    """
    Manages all serial connections.
    """

    # Will store the singleton here.
    __instance = None

    @staticmethod
    def get_instance():
        """
        Will return the manager instance.

        :return: The manager instance.
        """
        if Manager.__instance is None:
            Manager()
        return Manager.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Manager.__instance is not None:
            raise Exception("Only one instance of the manager should exist!")
        else:
            Manager.__instance = self

        # Will hold all connections.
        self._connections = {}  # type: Dict[str,SerialConnection]

    def setup_connection(self, device: str, listeners=[], baudrate=9600,
                         on_exit=[]):
        """
        Will setup a connection the given device.

        :param device: The device to connect to.
        :param listeners: The listeners to use.
        :param baudrate: The speed of the connection.
        :param on_exit: The listeners that will be called when the connection is lost.
        """
        if device in self._connections:
            raise Exception("Connection already exists")
        on_exit.append(_connection_closed_listener)
        self._connections[device] = SerialConnection(listeners, device,
                                                     baudrate, on_exit)
        self._connections[device].start()

    def get_listeners(self, device: str) -> SerialConnection:
        """
        Will get the listeners of the device.

        :param device: The device to get the listeners of.
        :return: The listeners.
        """
        return self._connections[device].listeners

    @property
    def connections(self) -> Dict[str, SerialConnection]:
        return self._connections

    @staticmethod
    def get_available_devices() -> List[str]:
        """
        Will list all connected comports.

        :return: List of connected comport devices.
        """
        devices = []
        for device in serial.tools.list_ports.comports():
            if "/dev/ttyAMA" not in device.device:
                devices.append(device.device)
        return devices

    def remove_connection(self, device: str):
        """
        Will remove the connection to a device.

        :param device: The device to disconnect with.
        """
        if device in self._connections:
            del self._connections[device]


def _connection_closed_listener(connection: SerialConnection):
    """
    Will be called if the connection was closed.

    :param connection: The connection that is being closed.
    """

    # Unregister the connection in the connection manager.
    manager = Manager.get_instance()  # type: Manager
    manager.remove_connection(connection.device)
