import logging
import sys
import kuring.settings.common as settings

"""Django DEVELOPMENT settings for kuring project."""

ALLOWED_HOSTS = []
DBCONFIG = '../config/db-dev.json'
DEBUG = True
MODE = 'Development Mode'

builder = settings.configurationConstructor(
    sys.modules[__name__],
    str(__file__).split('.')[0].split('/')[-1],
    DEBUG, ALLOWED_HOSTS, DBCONFIG
)

_l = logging.getLogger(__name__)
