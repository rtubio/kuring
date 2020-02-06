from __future__ import absolute_import, unicode_literals
import importlib.util
import os
import sys
from celery import Celery
from kuring import settings # import development, production


def loadEnvironment():
    # Adapted to support separate PRODUCTION and DEVELOPMENT configuration files
    # > For a development environment, set the environment variable '__DJ_DEVPROD' to 'dev'
    # > For a production environment, do nothing.

    if '__DJ_DEVPROD' in os.environ and os.environ['__DJ_DEVPROD'] == 'dev':
        environment = 'kuring.settings.development'
    else:
        environment = 'kuring.settings.production'

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', environment)
    return importlib.util.find_spec(environment).loader.load_module()

# First, the right module is loaded depending on whether Celery is executed for production or for development.
djcfg = loadEnvironment()

# Configuration file for CELERY, taken from:
#    https://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
# TODO # The backend has been specified explicitly as a parameter for the 'Celery' application constructor.
app = Celery('kuring', backend=djcfg.CELERY_CACHE_BACKEND)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
