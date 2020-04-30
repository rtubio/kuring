
import json
import os


"""Django COMMON settings for kuring project."""


def configurationConstructor(module, mode, debug, hosts, databaseConfig):

    builder = ConfigurationBuilder(mode, debug, hosts, databaseConfig)
    for k in builder.config:
        setattr(module, k, builder.config[k])
    return builder


class ConfigurationBuilder():

    def __init__(self, mode, debug, hosts, databaseConfig, loglevel='INFO'):
        """Basic constructor"""
        self.mode = mode
        self.debug = debug
        self.hosts = hosts
        self.dbconfig = databaseConfig
        self.config = {}
        self.loglevel = loglevel

        self.logger()
        self.django()
        self.database()
        self.celery()
        self.influxdb()

    def __str__(self):
        """This function prints a basic configuration status message."""
        return(f"> {self.mode}|{self.debug} :: hosts ({self.hosts})")

    def logger(self):
        """Django logger configuraiton"""
        # ### Logging settings
        self.config['LOGGING'] = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': '[{levelname} {asctime} {module} {process:d} {thread:d}] {message}',
                    'style': '{',
                },
            },
            'handlers': {
                'console': {
                    'level': self.loglevel,
                    'class': 'logging.StreamHandler',
                    # 'stream': sys.stdout,
                    'formatter': 'verbose',
                }
            },
            'loggers': {
                'django': {'level': self.loglevel, 'handlers': ['console'], 'propagate': False},
                'common': {'level': self.loglevel, 'handlers': ['console'], 'propagate': False},
                'kuring': {'level': self.loglevel, 'handlers': ['console'], 'propagate': False},
                'tasker': {'level': self.loglevel, 'handlers': ['console'], 'propagate': False}
            }
        }

    def database(self):
        """This function loads the configuration for the database from the given file."""

        with open(self.dbconfig) as file:
            db_secrets = json.load(file)

        self.config['DATABASES'] = {
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

    def celery(self, config='../conf/celery.json'):
        """This function loads the configuration for Celery from a given file"""
        # NOTE # for backend configuraiton: # 'redis://localhost:6379/0' # 'django-db'

        # ### CELERY configuration
        with open(config) as file:
            celery_cfg = json.load(file)

        self.config['CELERY_BROKER_URL'] = celery_cfg['broker']
        self.config['CELERY_RESULT_BACKEND'] = celery_cfg['backend']
        self.config['CELERY_CACHE_BACKEND'] = celery_cfg['backend-cache']
        self.config['CELERY_ACCEPT_CONTENT'] = celery_cfg['accept-content']
        self.config['CELERY_TASK_SERIALIZER'] = celery_cfg['task-serializer']
        self.config['CELERY_RESULT_SERIALIZER'] = celery_cfg['result-serializer']

    def influxdb(self, config='../.__skr__/influxdb.json'):
        """This function loads the configuration for InfluxDB from a given file"""

        # ### INFLUXDB configuration
        with open(config) as file:
            cfg = json.load(file)

        self.config['INFLUXDB_DBNAME'] = cfg['dbnx']
        self.config['INFLUXDB_ADMINPWD'] = cfg['admp']
        self.config['INFLUXDB_USRNAME'] = cfg['usrn']
        self.config['INFLUXDB_USRPWD'] = cfg['usrp']

    def django(self):

        # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
        self.config['BASE_DIR'] = os.path.dirname(os.path.dirname(os.path.abspath(os.path.join(__file__, '../.'))))

        # Static files (CSS, JavaScript, Images)
        # https://docs.djangoproject.com/en/3.0/howto/static-files/
        self.config['STATIC_ROOT'] = os.path.abspath(os.path.join(self.config['BASE_DIR'], '../static'))
        self.config['STATIC_URL'] = '/static/'

        # Routing
        self.config['ROOT_URLCONF'] = 'kuring.urls'
        self.config['WSGI_APPLICATION'] = 'kuring.wsgi.application'
        self.config['ASGI_APPLICATION'] = 'kuring.routing.application'

        # Site ID, see configuration for 'django.contrib.sites'
        self.config['SITE_ID'] = 1

        # Internationalization
        # https://docs.djangoproject.com/en/3.0/topics/i18n/
        self.config['LANGUAGE_CODE'] = 'en-us'
        self.config['TIME_ZONE'] = 'UTC'
        self.config['USE_I18N'] = True
        self.config['USE_L10N'] = True
        self.config['USE_TZ'] = True

        # SECURITY WARNING: keep the secret key used in production secret!
        with open('../.__skr__/django.json') as file:
            django_secrets = json.load(file)
        self.config['SECRET_KEY'] = django_secrets['djsk']

        # Application definition
        self.config['INSTALLED_APPS'] = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.sites',
            'django.contrib.staticfiles',
            # ### deps
            'bootstrap4',
            'django_icons',
            'channels',
            # ### 自分で
            'tasker'
        ]

        self.config['MIDDLEWARE'] = [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ]

        self.config['TEMPLATES'] = [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS':  [os.path.join(self.config['BASE_DIR'], 'kuring', 'templates')],
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
        self.config['AUTH_PASSWORD_VALIDATORS'] = [
            {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
            {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
            {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
            {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}
        ]

        self.config['CHANNEL_LAYERS'] = {
            'default': {
                'BACKEND': 'channels_redis.core.RedisChannelLayer',
                'CONFIG': {
                    'hosts': [('127.0.0.1', 6379)]
                }
            }
        }

        # Extra static file directories, outside of the common 'static' for all apps
        # https://docs.djangoproject.com/en/3.0/howto/static-files/
        self.config['STATICFILES_DIRS'] = [
            os.path.join(self.config['BASE_DIR'], "kuring", "static"),
            os.path.join(self.config['BASE_DIR'], "..", "node_modules", "bootstrap", "dist"),
            os.path.join(self.config['BASE_DIR'], "..", "node_modules", "font-awesome"),
            os.path.join(self.config['BASE_DIR'], "..", "node_modules", "plotly.js-dist"),
            os.path.join(self.config['BASE_DIR'], "..", "node_modules", "jquery", "dist"),
        ]
