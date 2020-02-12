
from asgiref.sync import async_to_sync
import channels.layers
import datetime
import random
import time

from celery import shared_task
from celery.utils.log import get_task_logger

from tasker import signals


COUNTER_MAX = 2000
logger = get_task_logger(__name__)
layer = channels.layers.get_channel_layer()


@shared_task(bind=True)
def add(self, x, y, counter=COUNTER_MAX):
    task_id = self.request.id
    async_to_sync(layer.group_add)('kuring', f'task_{task_id}')

    logger.info(f'Starting task (id = {task_id})')

    while (counter > 0):
        time.sleep(1)

        x = COUNTER_MAX - counter
        randA = random.randint(-10, 120)
        randB = random.randint(-10, 120)

        messageA = { 'type': 'plot.data', 'm': 'T1', 'x': x, 'y': randA }
        messageB = { 'type': 'plot.data', 'm': 'T2', 'x': x, 'y': randB }

        async_to_sync(layer.group_send)('kuring', messageA)
        async_to_sync(layer.group_send)('kuring', messageB)

        counter -= 1

    logger.info(f'Ending task (id = {task_id})')

    timestamp = datetime.datetime.now().timestamp()
    signals.taskFinished.send(sender='celeryTask', taskId=task_id, results={'timestamp': timestamp})
    message = { 'type': 'task.finished', 'task_id': task_id, 'timestamp': timestamp }
    async_to_sync(layer.group_send)('kuring', message)
    async_to_sync(layer.group_discard)('kuring', 'tasker')
