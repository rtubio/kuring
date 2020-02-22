
from asgiref.sync import async_to_sync
import channels.layers

from celery import shared_task
from celery.contrib.abortable import AbortableTask
from celery.utils.log import get_task_logger

from common import influxdb, time as _time
from drivers.ardoven import driver as ardoven_driver


COUNTER_MAX = 5000
_l = get_task_logger(__name__)
layer = channels.layers.get_channel_layer()


@shared_task
def influxdbWrite(taskpk, message):
    _l.debug(f"Writing to influxdb: {message}")
    ovendb = influxdb.CuringOven.retrieve(taskpk)
    ovendb.writePoint(message['m'], int(message['t']), message['y'])


@shared_task
def saveDelay(taskpk, timestamp, delay, jitter):
    _l.debug(f"Writing to influxdb: task#{taskpk} > delay (us): {delay} jitter (us): {jitter}")
    _l.debug(f'timestamp = {timestamp}, type(timestamp) = {type(timestamp)}')
    ovendb = influxdb.CuringOven.retrieve(taskpk)
    ovendb.saveDelay(timestamp, delay, jitter)


@shared_task()
def sendPlot(taskpk, sensorId, chunkSize=1024, channel_key='kuring'):
    """
    This function reads all the data for the plot from the database and returns it through a websocket in chunks of
    size 'chunkSize=1024'

    taskid -- identifier of the task
    sensorId -- identifier of the sensor whose data has been requested
    chunkSize=1024 -- maximum number of points to be sent to the user interface through websocket
    """
    group_key = f"task_{taskpk}"
    async_to_sync(layer.group_add)(channel_key, group_key)

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

        async_to_sync(layer.group_send)(channel_key, message)
        _l.debug(f"Sent {messageSize} points, [{sent, sent+messageSize}], until = {message['ts'][-1]}")

        sent += messageSize
        processed = 0
        message['ts'] = []
        message['vs'] = []

    async_to_sync(layer.group_discard)(channel_key, group_key)
    influxdb.CuringOven.cleanup(taskpk)


@shared_task(bind=True, base=AbortableTask)
def collectData(self, taskpk, counter=COUNTER_MAX, channel_key='kuring', wait=1):
    taskid = self.request.id
    _l.info(f'Starting task (id = {taskid})')

    group_key = f"task_{taskpk}"
    async_to_sync(layer.group_add)(channel_key, group_key)

    taskid = self.request.id
    _l.debug(f"Running driver task for <Ardoven>, with taskid = <{taskid}>")
    ardoven = ardoven_driver.ArdovenDriver(channel_key, group_key, taskpk)
    ardoven.load(self)
    ardoven.run()

    ardoven.stop()

    message = { 'type': 'task.finished', 'taskpk': taskpk, 'taskid': taskid, 'timestamp': _time.timestamp() }
    async_to_sync(layer.group_send)(channel_key, message)
    async_to_sync(layer.group_discard)(channel_key, group_key)
    influxdb.CuringOven.cleanup(taskpk)
