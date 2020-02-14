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
    """


    _clients = {}


    @staticmethod
    def retrieve(taskId):
        if taskId in CuringOven._clients:
            _l.debug(f"Retrieving client for task #{taskId}, clients.keys = {CuringOven._clients.keys()}")
            return CuringOven._clients[taskId]

        oven = CuringOven(taskId)
        CuringOven._clients[taskId] = oven
        _l.info(f"Added client for task #{taskId}, clients.keys = {CuringOven._clients.keys()}")
        return oven


    @staticmethod
    def cleanup(taskId):
        _l.info(f"Removing client for task #{taskId}, clients.keys = {CuringOven._clients.keys()}")
        try:
            oven = CuringOven._clients.pop(taskId)
            oven.close()
            oven = None
            _l.info(f"Removed client for task #{taskId}")
        except KeyError as ex:
            _l.warn(f"Exception = {ex}")
            _l.warn(f"No client for task #{taskId}, clients.keys = {CuringOven._clients.keys()}, skipping...")
            return


    def __init__(self, taskId):

        # This is the schema for the curing oven; this oven consists of a set of sensors for temperature, pressure
        # and frame closing status
        self.device = "testing"
        self.measurement = f"oven#{taskId}"
        self.fields = ['value']
        self.tags = ['device', 'sensor', 'variable']

        self._client = InfluxDBClient(
            username=settings.INFLUXDB_USRNAME,
            password=settings.INFLUXDB_USRPWD,
            database=settings.INFLUXDB_DBNAME
        )

        self.id_2_tags = {
            'T1': {'sensor': 'plate', 'variable': 'temperature', 'units': 'degC'},
            'T2': {'sensor': 'chamber', 'variable': 'temperature', 'units': 'degC'},
            'P1': {'sensor': 'bag', 'variable': 'pressure', 'units': 'psi'},
            'P2': {'sensor': 'chamber', 'variable': 'pressure', 'units': 'psi'},
            'O1': {'sensor': 'frame', 'variable': 'open', 'units': 'yes/no'}
        }

    def getMeasurement(self, sensorId, since=None, until=None):
        """
        This function returns a full measurement series taken by a given sensor, in between two specific points in
        time.

        sensorId -- predefined sensor identifier
        since=None -- (optional) timestamp describing the point after which the sensor data is required.
        until=None -- (optional) timestamp describing the point until which the sensor data is required.
        """
        tags = self.id_2_tags[sensorId]


    def writePoint(self, sensorId, timestamp, value):
        tags = self.id_2_tags[sensorId]
        point = {
            "measurement": self.measurement,
            "time": timestamp,
            "tags": {**tags, "device": self.device},
            "fields": {"value": value}
        }
        _l.info(f"point = {point}")
        self._client.write_points([point])
