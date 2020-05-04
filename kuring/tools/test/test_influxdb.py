from datetime import datetime as dt
import json
import logging
import unittest
from influxdb import InfluxDBClient

from common import influxdb, time as _time


class TestInfluxDb(unittest.TestCase):
    """
    Validation of the input/output of data with the InfluxDB database.
    """

    dbconfigFile = '../.__skr__/influxdb.json'
    testingDbname = 'testing-db'
    testingTaskId = 100
    testingSensorId = 'T1'
    testingValue = 1.0

    def _loadDbConfiguration(self):
        """
        Loads the configuration of the database.
        """
        with open(self.dbconfigFile) as file:
            self.dbConfig = json.load(file)

    def setUp(self):
        """
        The test set up method creates a temporal testing database at the existing InfluxDB client.
        """
        self._l = logging.getLogger(__name__)

        self._loadDbConfiguration()
        self._client = InfluxDBClient(username='admin', password=self.dbConfig['admp'])
        self._client.create_database(self.testingDbname)
        self._client.grant_privilege('all', self.testingDbname, self.dbConfig['usrn'])
        self._client.close()

    def tearDown(self):
        """
        Delete the testing database
        """
        self._client = InfluxDBClient(username='admin', password=self.dbConfig['admp'])
        self._client.drop_database(self.testingDbname)
        self._client.close()

    def test_writeread_isoformat(self):
        """
        This test validates that the writing of the data is performed correctly, so that it can be retrieved later on
        properly.
        """

        ovendb = influxdb.CuringOven.retrieve(self.testingTaskId, dbname=self.testingDbname)
        self.assertIsNotNone(ovendb)
        self.assertEqual(self.testingDbname, ovendb._client._database)  # check that we are not writing in other dbs

        ts = _time.timestamp()
        ts_dt = dt.fromtimestamp(ts)
        self._l.debug(f"WWW >> ts = {ts}, iso = {ts_dt.isoformat()}")

        ovendb.writePoint(self.testingSensorId, ts_dt.isoformat(), self.testingValue, time_precision='u')
        readout = ovendb.getMeasurement(self.testingSensorId)

        self._l.debug(f"readout = {readout}")
        ts_readout = _time.iso2timestamp(readout[0]['time'])
        ts_dt_readout = dt.fromtimestamp(ts_readout)
        self._l.debug(f"RRR >> ts = {ts_readout}, iso = {ts_dt_readout.isoformat()}")

        self.assertEqual(ts, ts_readout)
        self.assertEqual(ts_dt.isoformat(), ts_dt_readout.isoformat())

        ovendb.close()

    def test_writeread_timestamp(self):
        """
        This test validates that the writing of the data is performed correctly, so that it can be retrieved later on
        properly.
        """

        ovendb = influxdb.CuringOven.retrieve(self.testingTaskId, dbname=self.testingDbname)
        self.assertIsNotNone(ovendb)
        self.assertEqual(self.testingDbname, ovendb._client._database)  # check that we are not writing in other dbs

        ts = _time.timestamp()
        ts_dt = dt.fromtimestamp(ts)
        self._l.debug(f"WWW >> ts = {ts}, iso = {ts_dt.isoformat()}")

        ovendb.writePoint(self.testingSensorId, int(ts*1E6), self.testingValue, time_precision='u')
        readout = ovendb.getMeasurement(self.testingSensorId)

        self._l.debug(f"readout = {readout}")
        ts_readout = _time.iso2timestamp(readout[0]['time'])
        ts_dt_readout = dt.fromtimestamp(ts_readout)
        self._l.debug(f"RRR >> ts = {ts_readout}, iso = {ts_dt_readout.isoformat()}")

        self.assertEqual(ts, ts_readout)
        self.assertEqual(ts_dt.isoformat(), ts_dt_readout.isoformat())

        ovendb.close()


if __name__ == '__main__':
    unittest.main()
