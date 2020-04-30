from abc import ABC, abstractmethod
from asgiref.sync import async_to_sync
import channels
import logging


from common import influxdb, time as _time


class AbstractDriver(ABC):
    """
    Abstract class for drivers to use it as a stub.
    """

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


class GenericDriver(AbstractDriver):
    """
    Base class for the driver objects.

    Inheriting from this class permits the driver to interface with the system in an organized manner.
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
        self._l.info(f"Driver {__name__} loaded")

    def run(self):
        self._l.info(f"Driver {__name__} running")

    def stop(self):
        self._l.info(f"Driver {__name__} stopped")

    def pause(self):
        self._l.info(f"Driver {__name__} paused")

    def _notifyEvent(self, event, data):
        time = _time.timestamp()
        message = {'type': 'event.rx', 'taskpk': self._taskpk, 'event': event, 't': time, 'data': data}
        self._l.info(f"@ardoven.event - time = {time}, data = {data}")
        async_to_sync(self._c.group_send)(self._channelkey, message)

    def _notifyData(self, sensor, data):
        time = _time.timestamp()
        message = {'type': 'data.rx', 'taskpk': self._taskpk, 'm': sensor, 't': time, 'y': data}
        self._l.info(f"@ardoven.data - time = {time}, data = {data}")

        self._ovendb.writePoint(message['m'], int(message['t']*1000), message['y'])
        async_to_sync(self._c.group_send)(self._channelkey, message)
