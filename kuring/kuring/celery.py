from __future__ import absolute_import, unicode_literals
import importlib.util
import os
import sys
from celery import Celery
from kuring import settings # import development, production

# Configuration file for CELERY, taken from:
#    https://docs.celeryproject.org/en/latest/django/first-steps-with-django.html

# Adapted to support separate PRODUCTION and DEVELOPMENT configuration files
# > For a development environment, set the environment variable '__DJ_DEVPROD' to 'dev'
# > For a production environment, do nothing.
if os.environ['__DJ_DEVPROD'] == 'dev':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kuring.settings.development')
    spec = importlib.util.find_spec('kuring.settings.development')
    djcfg = spec.loader.load_module()
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kuring.settings.production')
    spec = importlib.util.find_spec('kuring.settings.production')
    djcfg = spec.loader.load_module()

app = Celery('kuring', backend=djcfg.CELERY_CACHE_BACKEND)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
