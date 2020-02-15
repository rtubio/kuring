from datetime import datetime as dt, timezone as tz

def timestamp(timezone=tz.utc):
    return dt.now().replace(tzinfo=timezone).timestamp()
