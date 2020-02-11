import json
import logging

from datetime import datetime
from django.db import models
from django.urls import reverse
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder

from tasker import signals

logger = logging.getLogger(__name__)


@receiver(signals.taskFinished)
def taskFinished(sender, taskId=None, results=None, **kwargs):
    logger.info(f"Task finished! Signal received from {sender}")

    object = Task.objects.get(task_id=taskId)
    object.status = Task.FINISHED
    object.results = json.dumps(results, cls=DjangoJSONEncoder)
    object.save()


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
