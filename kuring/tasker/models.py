import json
import logging

from channels.db import database_sync_to_async
from datetime import datetime
from django.db import models
from django.urls import reverse
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder

from tasker import signals, tasks

_l = logging.getLogger(__name__)


@receiver(signals.taskFinished)
def taskFinished(sender, taskId=None, results=None, **kwargs):
    _l.info(f"Task finished! Signal received from {sender}")
    object = Task.objects.get(task_id=taskId)

    object.status = Task.FINISHED
    object.results = json.dumps(results, cls=DjangoJSONEncoder)

    object.save()


@database_sync_to_async
def taskLaunched(taskId):
    _l.info(f"Task #{taskId} launched!")
    object = Task.objects.get(pk=taskId)

    if object.status == Task.NEW and not object.task_id:
        object.status = Task.RUNNING
        task_obj = tasks.collectData.delay()
        object.task_id = task_obj.id
        object.save()

    else:
        _l.error('Trying to launch task #{taskId} but its satus is not ready')


@database_sync_to_async
def taskStopped(taskId):
    _l.info(f"Task #{taskId} stopped!")
    object = Task.objects.get(pk=taskId)

    if object.status == Task.RUNNING and not object.task_id:
        object.status = Task.FINISHED
        obj.task_id = None
        object.save()

    else:
        _l.error('Trying to stop task #{taskId} but its satus is not ready')


class Task(models.Model):

    class Meta:
        ordering = ('created',)

    NEW = 'N'
    RUNNING = 'R'
    PAUSED = 'P'
    FINISHED = 'D'

    STATUS_CHOICES = [
        (NEW, 'New'), (RUNNING, 'Running'), (PAUSED, 'Paused'), (FINISHED, 'Finished'),
    ]

    name = models.CharField(
        default='', max_length=100,
        verbose_name='Name of the experiment, to be used as a reference'
    )
    created = models.DateTimeField(
        default=datetime.now, editable=False, blank=True,
        verbose_name='Date of creation of the experiment object'
    )

    status = models.CharField(
        default=NEW, editable=False, max_length=1, choices=STATUS_CHOICES,
        verbose_name="Execution status for this experiment, 1 character among the available options")

    task_id = models.CharField(
        default='', max_length=255, null=True, blank=True, editable=False,
        verbose_name="Identifier of the task launched with Celery for the experiment execution"
    )

    result = models.TextField(default='', blank=False, verbose_name="Task result, serialized JSON object")

    def get_absolute_url(self):
        return reverse('dashboard')

    def __unicode__(self):
        return self.name
