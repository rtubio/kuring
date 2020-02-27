from datetime import datetime as dt, timezone as tz
from dateutil import parser


def timestamp(timezone=tz.utc):
    return dt.now().replace(tzinfo=timezone).timestamp()


def iso2timestamp(isoString):
    return parser.isoparse(isoString).timestamp()


def utctimestamp2iso(timestamp):
    return dt.utcfromtimestamp(timestamp).isoformat()
