from __future__ import absolute_import, unicode_literals
import os
import sys
from celery import Celery

# Configuration file for CELERY, taken from:
#    https://docs.celeryproject.org/en/latest/django/first-steps-with-django.html

# Adapted to support separate PRODUCTION and DEVELOPMENT configuration files
# > For a development environment, set the environment variable '__DJ_DEVPROD' to 'dev'
# > For a production environment, do nothing.
if os.environ['__DJ_DEVPROD'] == 'dev':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kuring.settings.development')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kuring.settings.production')

app = Celery('kuring', backend='redis://localhost:6379')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
