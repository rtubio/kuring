from django.conf import settings
from influxdb import InfluxDBClient
import logging


_l = logging.getLogger(__name__)


""" JSON body example
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
    This object acts as an interface
    """


    _clients = {}


    @staticmethod
    def retrieve(taskId):
        if taskId in CuringOven._clients:
            return CuringOven._clients[taskId]

        oven = CuringOven(taskId)
        CuringOven._clients[taskId] = oven
        return oven


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
