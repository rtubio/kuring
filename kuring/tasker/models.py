import logging

from celery.contrib.abortable import AbortableAsyncResult
from channels.db import database_sync_to_async
from datetime import datetime
from django.db import models
from django.urls import reverse
from django.utils import timezone


_l = logging.getLogger(__name__)


NEW = 'N'
RUNNING = 'R'
PAUSED = 'P'
FINISHED = 'D'

STATUS_CHOICES = [
    (NEW, 'New'), (RUNNING, 'Running'), (PAUSED, 'Paused'), (FINISHED, 'Finished'),
]


class Events(models.Model):

    class Meta:
        ordering = ('timestamp',)

    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name="Timestamp marking when the event occurred, autofilled by model creation"
    )

    event = models.CharField(
        default=RUNNING, editable=False, max_length=1, choices=STATUS_CHOICES,
        verbose_name="Execution status for this experiment, 1 character among the available options"
    )


class Task(models.Model):

    class Meta:
        ordering = ('created',)

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
        verbose_name="Execution status for this experiment, 1 character among the available options"
    )

    events = models.ManyToManyField(
        Events,
        verbose_name="List of events related with the execution lifecycle of this task"
    )

    task_id = models.CharField(
        default='', max_length=255, null=True, blank=True, editable=False,
        verbose_name="Identifier of the task launched with Celery for the experiment execution"
    )

    result = models.TextField(default='', blank=False, verbose_name="Task result, serialized JSON object")

    def get_absolute_url(self):
        return reverse('dashboard')

    def __unicode__(self):
        return self.name


@database_sync_to_async
def taskLaunched(taskpk, taskid):
    _l.info(f"Task #{taskpk} launched!")
    obj = Task.objects.get(pk=taskpk)

    if obj.status == NEW:

        event = Events.objects.create()
        obj.events.add(event)

        obj.status = RUNNING
        obj.task_id = taskid
        obj.save()

    else:
        _l.error(f'Trying to launch task #{taskid} but its satus is not ready')


@database_sync_to_async
def taskFinished(taskpk, abort=False):
    """
    This method permits stopping a task once it has finished. Stopping the task means two actions: (1) update the
    state of the task in the Django ORM's managed databased; and (2) stop the celery task itself.
    Since any task can be stopped because of two different reasons (A ~ user request on the UI, B ~ the celery task
    finishes by itself), an abort flag is added to the method to indicate when the latter should also stop the celery
    task or not. Usually, this flag is convenient for whenever the stop request for the task comes from the UI.

    taskpk -- identifier of the task object within Django's ORM database
    abort=False -- flag that indicates whether this method should also abort the celery task or not
    """
    _l.info(f"Task #{taskpk} stopped!")
    obj = Task.objects.get(pk=taskpk)

    if obj.status == RUNNING:
        obj.status = FINISHED

        if abort:
            abortable_task = AbortableAsyncResult(obj.task_id)
            abortable_task.abort()

        event = Events.objects.create()
        event.event = FINISHED
        event.save()

        obj.events.add(event)

        obj.save()

    else:
        _l.error(f'Trying to stop task for object #{taskpk} but its satus is not ready')
