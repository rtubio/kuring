import serial

from drivers import generic


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


class ArdovenDriver(generic.GenericDriver):

    type = -1
    serialPort = '/dev/arduino'
    timeout = 1
    speed = 115200

    TYPE_2_SENSOR = {0: 'T1', 1: 'T2', 2: 'O0'}

    def __init__(self, *args, **kwargs):
        super(ArdovenDriver, self).__init__(__name__, *args, **kwargs)

    def load(self, *args, **kwargs):

        self._serial = serial.Serial(self.serialPort, self.speed, timeout=self.timeout)
        self._serial.flushInput()

        return super(ArdovenDriver, self).load(*args, **kwargs)

    def _sendStartCommand(self):
        self._sendCommand(C_START)

    def _sendStopCommand(self):
        self._sendCommand(C_STOP)

    def _sendCommand(self, commandType):
        commandString = str(MARKER_MESSAGE) + str(commandType)
        self._serial.write(commandString.encode('utf-8'))
        self._serial.flush()

    def stop(self, *args, **kwargs):
        super(ArdovenDriver, self).stop(*args, **kwargs)
        self._sendStopCommand()
        self._serial.close()

    def run(self, *args, **kwargs):
        super(ArdovenDriver, self).run(*args, **kwargs)
        ser_bytes = None
        sensor = None

        while not self._abort.is_aborted():

            try:

                ser_bytes = self._serial.readline()
                start = int(ser_bytes[0:MARKER_LEN-1].decode('utf-8'))
                self._l.debug(f"START MARKER: start={start}, MARKER={MARKER_MESSAGE}")

                if start == MARKER_MESSAGE:
                    type = int(ser_bytes[MARKER_LEN-1:MARKER_LEN].decode("utf-8"))
                    self._l.debug(f'MESSAGE type = {type}')

                    if type == EVENT_TYPE:

                        etype = int(ser_bytes[MARKER_LEN:MARKER_LEN+1].decode("utf-8"))
                        payload = int(ser_bytes[MARKER_LEN+1:MARKER_LEN+2].decode("utf-8"))
                        self._l.debug(f"EVENT, bytes: {ser_bytes}, start: {start}, ety = {etype} epl: {payload}")

                        if etype == E_SYSWAITING:
                            self._sendStartCommand()

                        self._notifyEvent(etype, payload)

                    else:

                        sensorChar = int(ser_bytes[MARKER_LEN:MARKER_LEN+1].decode("utf-8"))
                        sensor = self.TYPE_2_SENSOR[sensorChar]
                        data = float(ser_bytes[MARKER_LEN+1:len(ser_bytes)-2].decode("utf-8"))
                        self._l.debug(f"DATA, bytes: {ser_bytes}, start: {start}, t = {type} data: {data}")

                        self._notifyData(sensor, data)

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

        self._l.info(f"Driver <{self.driverName}> ending run!")
