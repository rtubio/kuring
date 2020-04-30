from abc import ABC, abstractmethod
from asgiref.sync import async_to_sync
import channels
import logging
import serial


from common import influxdb, time as _time


class AbstractDriver(ABC):
    """Abstract class for drivers to use it as a stub."""

    @abstractmethod
    def load(self, abort):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def _notifyEvent(self, event, data):
        pass

    @abstractmethod
    def _notifyData(self, sensor, data):
        pass


class BaseDriver(AbstractDriver):
    """
    Base class for the driver objects, manages interconnection of the drivers with the rest of the infrastructure.
    """

    def __init__(self, name, channelkey, groupkey, taskpk, **kwargs):
        self.driverName = name

        self._l = logging.getLogger(self.driverName)
        self._c = channels.layers.get_channel_layer()

        self._channelkey = channelkey
        self._groupkey = groupkey
        self._taskpk = taskpk
        async_to_sync(self._c.group_add)(self._channelkey, self._groupkey)

        self._ovendb = influxdb.CuringOven.retrieve(self._taskpk)

        self._l.info(f"Driver {self.driverName} initialized")

    def load(self, abort):
        self._abort = abort
        self._l.info(f"Driver {self.driverName} loaded")

    def run(self):
        self._l.info(f"Driver <{self.driverName}> started run!")

    def stop(self):
        self._l.info(f"Driver {self.driverName} stopped")

    def pause(self):
        self._l.info(f"Driver {self.driverName} paused")

    def _notifyEvent(self, event, data):
        message = {'type': 'event.rx', 'taskpk': self._taskpk, 'event': event, 't': _time.timestamp(), 'data': data}
        async_to_sync(self._c.group_send)(self._channelkey, message)
        self._l.info(f"EVENT, message = {message}")

    def _notifyData(self, message):
        message['t'] = _time.timestamp()
        message['taskpk'] = self._taskpk
        message['type'] = 'data.rx'

        self._ovendb.writePoint(message['m'], int(message['t']*1000), message['y'])
        async_to_sync(self._c.group_send)(self._channelkey, message)

        self._l.info(f"DATA, message = {message}")


class SerialSlaveDriver(BaseDriver):
    """
    This class implements a driver that can command a remote device and receive its telemetry.
    The command / telemetry transmission / reception system has been specifically standardized for this system.
    """

    MARKER_LEN = 5
    MARKER_MESSAGE = 0x1FF1
    DATA_TYPE = 0
    EVENT_TYPE = 1
    COMMAND_TYPE = 2

    C_PAUSE = 1
    C_RESUME = 2
    C_STOP = 3
    C_START = 4
    C_ENABLE_SERIAL = 5
    C_DISABLE_SERIAL = 6

    E_SYSREADY = 1
    E_SYSWAITING = 2
    E_SYSPAUSED = 3
    E_SYSHALTING = 4
    E_SYSHALTED = 5
    E_THERMALOFF = 6
    E_THERMALONPAUSED = 7
    E_THERMALON = 8
    E_ERR_MARKERDIFFERS = 10
    E_ERR_UNSUPPORTEDCOMMAND = 11

    def __init__(self, port, speed, timeout, sensor_types, *args, **kwargs):
        super(SerialSlaveDriver, self).__init__(*args, **kwargs)

        self.port = port
        self.speed = speed
        self.timeout = timeout
        self.sensor_types = sensor_types

    def load(self, *args, **kwargs):
        super(SerialSlaveDriver, self).load(*args, **kwargs)

        self._serial = serial.Serial(self.port, self.speed, timeout=self.timeout)
        self._serial.flushInput()

        return super(SerialSlaveDriver, self).load(*args, **kwargs)

    def stop(self, *args, **kwargs):
        super(SerialSlaveDriver, self).stop(*args, **kwargs)

        self._sendStopCommand()
        self._serial.close()

    def _sendStartCommand(self):
        self._sendCommand(SerialSlaveDriver.C_START)

    def _sendStopCommand(self):
        self._sendCommand(SerialSlaveDriver.C_STOP)

    def _sendCommand(self, commandType):
        commandString = str(SerialSlaveDriver.MARKER_MESSAGE) + str(commandType)
        self._serial.write(commandString.encode('utf-8'))
        self._serial.flush()

    def run(self, *args, **kwargs):
        super(SerialSlaveDriver, self).run(*args, **kwargs)

        ser_bytes = None
        sensor = None

        while not self._abort.is_aborted():

            try:

                ser_bytes = self._serial.readline()
                start = int(ser_bytes[0:self.MARKER_LEN-1].decode('utf-8'))
                self._l.debug(f"START MARKER: start={start}, MARKER={self.MARKER_MESSAGE}")

                if start == self.MARKER_MESSAGE:
                    type = int(ser_bytes[self.MARKER_LEN-1:self.MARKER_LEN].decode("utf-8"))
                    self._l.debug(f'MESSAGE type = {type}')

                    if type == self.EVENT_TYPE:

                        etype = int(ser_bytes[self.MARKER_LEN:self.MARKER_LEN+1].decode("utf-8"))
                        payload = int(ser_bytes[self.MARKER_LEN+1:self.MARKER_LEN+2].decode("utf-8"))
                        self._l.debug(f"EVENT, bytes: {ser_bytes}, start: {start}, ety = {etype} epl: {payload}")

                        if etype == self.E_SYSWAITING:
                            self._sendStartCommand()

                        self._notifyEvent(etype, payload)

                    else:

                        sensorChar = int(ser_bytes[self.MARKER_LEN:self.MARKER_LEN+1].decode("utf-8"))
                        sensor = self.sensor_types[sensorChar]
                        data = float(ser_bytes[self.MARKER_LEN+1:len(ser_bytes)-2].decode("utf-8"))
                        self._l.debug(f"DATA, bytes: {ser_bytes}, start: {start}, t = {type} data: {data}")

                        message = {'m': sensor, 'y': data}
                        self._notifyData(message)

                else:
                    self._l.debug(ser_bytes)
                    type = -1
                    continue

            except KeyError as ex:
                self._l.warning(f"<{type}> is unsupported, dropping data = {ser_bytes.decode('utf-8')}, ex = {ex}")
                type = -1
                continue
            except ValueError:
                self._l.warning(f"Log message from ardoven: {ser_bytes}")
                type = -1
                continue
            except Exception as ex:
                self._l.warning(f"Excepton ex = {ex}, serialData = {ser_bytes}")
                type = -1
                continue

        self._l.info(f"Driver <{self.driverName}> ended run!")
