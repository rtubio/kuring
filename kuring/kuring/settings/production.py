
import sys
import kuring.settings.common as settings

"""Django PRODUCTION settings for kuring project."""

ALLOWED_HOSTS = []
DBCONFIG = '../.__skr__/db.json'
DEBUG = True
MODE = 'Production Mode'

logging.basicConfig(level=logging.INFO)
_l = logging.getLogger(__name__)

settings.configurationConstructor(
    sys.modules[__name__],
    str(__file__).split('.')[0].split('/')[-1],
    DEBUG, ALLOWED_HOSTS, DBCONFIG
)
_l.info(f"settings - {builder}")
