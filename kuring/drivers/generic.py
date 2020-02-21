from asgiref.sync import async_to_sync
import channels
import logging


from common import time as _time


class Driver(object):
    """
    Base class for the driver objects.

    Inheriting from this class permits the driver to interface with the system in an organized manner.
    """

    def __init__(self, name, channelkey, groupkey, taskpk, **kwargs):
        self.driverName = name

        self._l = logging.getLogger(self.driverName)
        self._c = channels.layers.get_channel_layer()
        self._t0 = self._getTimestamp()

        self._channelkey = channelkey
        self._groupkey = groupkey
        self._taskpk = taskpk
        async_to_sync(self._c.group_add)(self._channelkey, self._groupkey)

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
        time = self._getTimestamp()
        message = { 'type': 'event.rx', 'taskpk': self._taskpk, 'event': event, 't': time, 'data': data }
        async_to_sync(self._c.group_send)(self.channelkey, message)

    def _notifyData(self, sensor, data):
        time = self._getTimestamp()
        x = time - self._t0
        message = { 'type': 'data.rx', 'taskpk': self._taskpk, 'm': sensor, 't': time, 'x': x, 'y': data }
        async_to_sync(self._c.group_send)(self._channelkey, message)

    def _getTimestamp(self):
        return _time.timestamp()
