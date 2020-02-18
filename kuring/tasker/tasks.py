
from asgiref.sync import async_to_sync
import channels.layers
import datetime
import math
import time

from celery import current_app, shared_task
from celery.contrib.abortable import AbortableTask
from celery.utils.log import get_task_logger

from common import influxdb, time as _time


COUNTER_MAX = 5000
_l = get_task_logger(__name__)
layer = channels.layers.get_channel_layer()


@shared_task
def influxdbWrite(taskpk, message):
    _l.debug(f"Writing to influxdb: {message}")
    ovendb = influxdb.CuringOven.retrieve(taskpk)
    ovendb.writePoint(message['m'], message['x'], message['y'])


@shared_task
def saveDelay(taskpk, timestamp, delay, jitter):
    _l.debug(f"Writing to influxdb: task#{taskpk} > delay (us): {delay} jitter (us): {jitter}")
    _l.debug(f'timestamp = {timestamp}, type(timestamp) = {type(timestamp)}')
    ovendb = influxdb.CuringOven.retrieve(taskpk)
    ovendb.saveDelay(timestamp, delay, jitter)


@shared_task(base=AbortableTask)
def sendPlot(taskpk, sensorId, chunkSize=1024):
    """
    This function reads all the data for the plot from the database and returns it through a websocket in chunks of
    size 'chunkSize=1024'

    taskid -- identifier of the task
    sensorId -- identifier of the sensor whose data has been requested
    chunkSize=1024 -- maximum number of points to be sent to the user interface through websocket
    """
    group_key = f"task_{taskpk}"
    async_to_sync(layer.group_add)('kuring', group_key)

    _l.info(f"[TASK.sendPlot] task = {taskpk}, sensorId = {sensorId}")
    ovendb = influxdb.CuringOven.retrieve(taskpk)
    measurement = ovendb.getMeasurement(sensorId)

    points = len(measurement)
    sent = 0
    processed = 0
    messageSize = chunkSize     # default, to be adjusted for the last iteration
    message = {'type': 'replay.data', 'taskpk': taskpk, 'm': sensorId, 'ts': [], 'vs': []}

    while (sent < points):
        left = points - sent
        if left < chunkSize:
            messageSize = left

        while (processed < messageSize):
            message['ts'].append(_time.iso2timestamp(measurement[sent+processed]['time']))
            message['vs'].append(measurement[sent+processed]['value'])
            processed += 1
            # _l.debug(f"~~~~~ processed = {processed}, message = {message}")

        async_to_sync(layer.group_send)('kuring', message)
        _l.debug(f"Sent {messageSize} points, [{sent, sent+messageSize}], until = {message['ts'][-1]}")

        sent += messageSize
        processed = 0
        message['ts'] = []
        message['vs'] = []

    async_to_sync(layer.group_discard)('kuring', group_key)
    influxdb.CuringOven.cleanup(taskpk)


@shared_task(bind=True, base=AbortableTask)
def collectData(self, taskpk, counter=COUNTER_MAX):
    taskid = self.request.id
    group_key = f"task_{taskpk}"
    async_to_sync(layer.group_add)('kuring', group_key)

    _l.info(f'Starting task (id = {taskid})')

    while counter > 0 and not self.is_aborted():
        time.sleep(1)

        x = COUNTER_MAX - counter
        yA = math.cos(x)
        yB = math.sin(x)

        messageA = { 'type': 'plot.data', 'taskpk': taskpk, 'm': 'T1', 'x': x, 'y': yA, 't': _time.timestamp() }
        messageB = { 'type': 'plot.data', 'taskpk': taskpk, 'm': 'T2', 'x': x, 'y': yB, 't': _time.timestamp() }

        influxdbWrite.delay(taskpk, messageA)
        influxdbWrite.delay(taskpk, messageB)

        async_to_sync(layer.group_send)('kuring', messageA)
        async_to_sync(layer.group_send)('kuring', messageB)

        counter -= 1

    if self.is_aborted():
        _l.info(f'ABORTING task (id = {taskid})')
    else:
        _l.info(f'Ending task (id = {taskid})')

    message = { 'type': 'task.finished', 'taskpk': taskpk, 'taskid': taskid, 'timestamp': _time.timestamp() }
    async_to_sync(layer.group_send)('kuring', message)
    async_to_sync(layer.group_discard)('kuring', group_key)
    influxdb.CuringOven.cleanup(taskpk)
