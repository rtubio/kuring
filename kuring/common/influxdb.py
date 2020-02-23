from django.conf import settings
from influxdb import InfluxDBClient
import logging


_l = logging.getLogger(__name__)


""" JSON body example, taken from: https://influxdb-python.readthedocs.io/en/latest/examples.html
        json_body = [{
            "measurement": "test#cpu_load_short",
            "tags": {
                "host": "server01",
                "region": "us-west"
            },
            "time": "2009-11-10T23:00:00Z",
            "fields": {
                "Float_value": 0.64,
                "Int_value": 3,
                "String_value": "Text",
                "Bool_value": True
            }
        }]
"""


class CuringOven(object):
    """
    This object acts as an interface with the InfluxDB database for the data coming from the curing oven.

    NOTICE: in order to avoid further confusion when it comes to write / read data from the InfluxDB database, the
    following convention is adopted:

    a) write methods > they will receive the timestamp as an integer with the number of miliseconds and transform
                        it into an ISO datetime string to write it into the database
    b) read methods > they will return the list of points "as they are" read from the database
    """

    _clients = {}

    @staticmethod
    def retrieve(taskId, dbname=None):
        if taskId in CuringOven._clients:
            _l.debug(f"[GOT] InfluxDB client for task #{taskId}, clients.keys = {CuringOven._clients.keys()}")
            return CuringOven._clients[taskId]

        oven = CuringOven(taskId, dbname=dbname)
        CuringOven._clients[taskId] = oven
        _l.debug(f"[ADDED] InfluxDB client for task #{taskId}, clients.keys = {CuringOven._clients.keys()}")
        return oven

    @staticmethod
    def cleanup(taskId):
        try:
            oven = CuringOven._clients.pop(taskId)
            _l.debug(f'[CLEANUP] oven = {oven}')
            oven.close()
            oven = None
            _l.debug(f"[REMOVED] InfluxDB client for task #{taskId}, clients.keys = {CuringOven._clients.keys()}")
        except KeyError as ex:
            _l.warn(f"Exception = {ex}")
            _l.warn(f"No client for task #{taskId}, clients.keys = {CuringOven._clients.keys()}, skipping...")
            return

    def __init__(self, taskId, dbname=None):

        # This is the schema for the curing oven; this oven consists of a set of sensors for temperature, pressure
        # and frame closing status
        self.device = "testing"
        self.measurement = f"oven#{taskId}"
        self.fields = ['value']
        self.tags = ['device', 'sensor', 'variable']

        _l.debug(f"settings: {settings.INFLUXDB_DBNAME}")

        if dbname:
            influxdbname = dbname
        else:
            influxdbname = settings.INFLUXDB_DBNAME

        self._client = InfluxDBClient(
            username=settings.INFLUXDB_USRNAME,
            password=settings.INFLUXDB_USRPWD,
            database=influxdbname
        )

        self.sensorId_2_tags = {
            'T1': {'sensor': 'plate', 'variable': 'temperature', 'units': 'degC'},
            'T2': {'sensor': 'chamber', 'variable': 'temperature', 'units': 'degC'},
            'P1': {'sensor': 'bag', 'variable': 'pressure', 'units': 'psi'},
            'P2': {'sensor': 'chamber', 'variable': 'pressure', 'units': 'psi'},
            'O1': {'sensor': 'frame', 'variable': 'open', 'units': 'yes/no'},
            'JD': {'sensor': 'dj-js', 'variable': 'delay', 'units': 'us'},
            'JJ': {'sensor': 'dj-js', 'variable': 'jitter', 'units': 'us'}
        }

        self.tags_2_sensorId = {
            'plate': {'temperature': 'T1'},
            'chamber': {'temperature': 'T2', 'pressure': 'P2'},
            'bag': {'pressure': 'P1'},
            'frame': {'open': 'O1'},
            'dj-ds': {'delay': 'JD'},
            'dj-js': {'jitter': 'JJ'}
        }

    def close(self):
        self._client.close()

    def getMeasurement(self, sensorId):
        """
        This function returns a full measurement series taken by a given sensor, in between two specific points in
        time.

        sensorId -- predefined sensor identifier
        """
        tags = self.sensorId_2_tags[sensorId]
        query = self._client.query(f"select * from \"{self.measurement}\"")
        return list(query.get_points(tags=tags))

    def writePoint(self, sensorId, timestamp, value, time_precision='ms'):
        tags = self.sensorId_2_tags[sensorId]
        point = {
            "measurement": self.measurement,
            "time": timestamp,
            "tags": {**tags, "device": self.device},
            "fields": {"value": value}
        }
        self._client.write_points([point], time_precision=time_precision)

    def saveDelay(self, timestamp, delay, jitter):
        self.writePoint('JD', timestamp, delay)
        self.writePoint('JJ', timestamp, jitter)
