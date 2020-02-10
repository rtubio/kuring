
import time

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def add(x, y):
    logger.info('Starting task...')
    time.sleep(10)
    logger.info('Ending task...')
    return x + y
