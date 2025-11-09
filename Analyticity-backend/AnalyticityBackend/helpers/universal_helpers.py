import pytz
from datetime import datetime

from constants.universal_constants import LOCAL_TZ


def convert_utc_to_local(utc_time_input):
    """
    Converts a UTC time (string or datetime) to local time (e.g., Europe/Prague)
    """
    if isinstance(utc_time_input, str):
        utc_time = datetime.strptime(utc_time_input, "%Y-%m-%dT%H:%M:%SZ")
    elif isinstance(utc_time_input, datetime):
        utc_time = utc_time_input
    else:
        raise ValueError("Unsupported time format")

    utc_time = utc_time.replace(tzinfo=pytz.UTC)
    local_tz = pytz.timezone("Europe/Prague")
    local_time = utc_time.astimezone(local_tz)
    return local_time.strftime("%Y-%m-%d %H:%M:%S")
