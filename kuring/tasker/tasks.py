
import datetime
import time

from celery import shared_task
from celery.utils.log import get_task_logger

from tasker import signals

logger = get_task_logger(__name__)


@shared_task(bind=True)
def add(self, x, y):
    task_id = self.request.id

    logger.info(f'Starting task (id = {task_id})')
    time.sleep(5)

    logger.info(f'Ending task (id = {task_id})')
    signals.taskFinished.send(sender='celeryTask', taskId=task_id, results={'timestamp': datetime.datetime.now()})
