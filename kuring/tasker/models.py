from datetime import datetime
from django.db import models
from django.urls import reverse


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

    def get_absolute_url(self):
        return reverse('dashboard')

    def __unicode__(self):
        return self.name
