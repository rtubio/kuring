
from asgiref.sync import async_to_sync
import datetime
import time

from celery import shared_task
from celery.utils.log import get_task_logger

from tasker import signals


logger = get_task_logger(__name__)
# layer = channels.layers.get_channel_layer()


@shared_task(bind=True)
def add(self, layer, x, y):
    counter = 5
    task_id = self.request.id
    async_to_sync(layer.group_add)('kuring', f'task_{task_id}')

    logger.info(f'Starting task (id = {task_id})')

    message = { 'type': 'plot', 'f': 'f1', 'm': 'temp_x1', 'x': 100, 'y': 50}
    while (counter > 0):
        time.sleep(5)
        async_to_sync(layer.group_send)('kuring', message)
        counter -= 1

    logger.info(f'Ending task (id = {task_id})')
    signals.taskFinished.send(sender='celeryTask', taskId=task_id, results={'timestamp': datetime.datetime.now()})
    async_to_sync(layer.group_discard)('kuring', 'tasker')
