from datetime import datetime as dt, timezone as tz
from dateutil import parser


def timestamp(timezone=tz.utc):
    return dt.now().replace(tzinfo=timezone).timestamp()


def iso2timestamp(isoString):
    return parser.isoparse(isoString).timestamp()
