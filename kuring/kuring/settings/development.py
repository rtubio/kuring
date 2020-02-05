
import json
import os
import sys
import kuring.settings.common as settings

"""Django DEVELOPMENT ettings for kuring project."""

ALLOWED_HOSTS = []
DBCONFIG = '../config/db-dev.json'
DEBUG = True
LOG_LEVEL = 'INFO'
MODE = str(__file__).split('.')[0].split('/')[-1]

settings.printConfiguration(MODE, DEBUG, LOG_LEVEL, ALLOWED_HOSTS)

BASE_DIR = settings.BASE_DIR
SITE_ID = settings.SITE_ID
SECRET_KEY = settings.SECRET_KEY
INSTALLED_APPS = settings.INSTALLED_APPS
MIDDLEWARE = settings.MIDDLEWARE
ROOT_URLCONF = settings.ROOT_URLCONF
TEMPLATES = settings.TEMPLATES
WSGI_APPLICATION = settings.WSGI_APPLICATION
AUTH_PASSWORD_VALIDATORS = settings.AUTH_PASSWORD_VALIDATORS

LANGUAGE_CODE = settings.LANGUAGE_CODE
TIME_ZONE = settings.TIME_ZONE
USE_I18N = settings.USE_I18N
USE_L10N = settings.USE_L10N
USE_TZ = settings.USE_TZ

STATIC_URL = settings.STATIC_URL
STATIC_ROOT = settings.STATIC_ROOT

CELERY_BROKER_URL = settings.CELERY_BROKER_URL
# CELERY_RESULT_BACKEND = settings.CELERY_RESULT_BACKEND
# CELERY_ACCEPT_CONTENT = settings.CELERY_ACCEPT_CONTENT
# CELERY_TASK_SERIALIZER = settings.CELERY_TASK_SERIALIZER
# CELERY_RESULT_SERIALIZER = settings.CELERY_RESULT_SERIALIZER

DATABASES = settings.loaddb(DBCONFIG)
LOGGING = settings.configureBasicLogger(LOG_LEVEL)
