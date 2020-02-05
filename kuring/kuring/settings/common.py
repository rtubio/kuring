
import json
import os
import sys


"""Django COMMON settings for kuring project."""


def printConfiguration(mode, debug, loglevel, hosts):
    """This function prints a basic configuration status message."""
    print(f"> Executing in {mode} mode: debug ({debug}), hosts ({hosts}), loglevel ({loglevel})")
    print(f"> BASE_DIR ({BASE_DIR}), STATIC_ROOT ({STATIC_ROOT})")


def configureBasicLogger(loglevel):
    """This function creates a basic logging object."""

    return {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'formatters': {
            'verbose': {
                'format': '%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(module)s %(process)d %(thread)d %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': loglevel,
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'django':{
                'level': loglevel,
                'handlers': ['console'],
                'propagate': True,
            },
           'gunicorn.errors': {
                'level': loglevel,
                'handlers': ['console'],
                'propagate': True,
            }
        },
    }


def loaddb(dbconfig):
    """This function loads the configuration for the database from the given file."""

    with open(dbconfig) as file:
        db_secrets = json.load(file)

    return {
        'default': {
            'ENGINE': db_secrets['ngin'],
            'NAME': db_secrets['name'],
            'USER': db_secrets['user'],
            'PASSWORD': db_secrets['pass'],
            'HOST': db_secrets['host'],
            'PORT': db_secrets['port'],
            'TEST': {
                'CHARSET': 'utf8',
                'COLLATION': 'utf8_general_ci',
            }
        }
    }


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.path.join(__file__, '../.'))))

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, '../static'))
STATIC_URL = '/static/'

# Routing
ROOT_URLCONF = 'kuring.urls'
WSGI_APPLICATION = 'kuring.wsgi.application'

# Site ID, see configuration for 'django.contrib.sites'
SITE_ID = 1

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# SECURITY WARNING: keep the secret key used in production secret!
with open('../.__skr__/django.json') as file:
    django_secrets = json.load(file)
SECRET_KEY = django_secrets['djsk']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    ### 自分で
    'django_celery_results',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS':  [os.path.join(BASE_DIR, 'kuring', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# ### CELERY configuration
with open('../config/celery.json') as file:
    celery_secrets = json.load(file)
CELERY_BROKER_URL = celery_secrets['broker']
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0' # 'django-db'
# CELERY_CACHE_BACKEND = 'django-cache'

# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
