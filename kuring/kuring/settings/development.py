
import sys
import kuring.settings.common as settings

"""Django DEVELOPMENT settings for kuring project."""

ALLOWED_HOSTS = []
DBCONFIG = '../config/db-dev.json'
DEBUG = True
LOG_LEVEL = 'INFO'
MODE = 'Development Mode'

settings.configurationConstructor(
    sys.modules[__name__],
    str(__file__).split('.')[0].split('/')[-1],
    DEBUG, ALLOWED_HOSTS, DBCONFIG, LOG_LEVEL
)
