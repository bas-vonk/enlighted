from datetime import datetime
from time import mktime, time
from typing import Dict

from requests.models import PreparedRequest

SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = 60 * SECONDS_IN_MINUTE
SECONDS_IN_DAY = 24 * SECONDS_IN_HOUR


def ts_str_to_unix(timestamp_str: str, timestamp_str_format: str) -> int:
    """Convert a datetime string to unix timestamp."""
    return int(
        mktime(datetime.strptime(timestamp_str, timestamp_str_format).timetuple())
    )


def now() -> int:
    """Get current timestamp in unix."""
    return int(time())


def last_full_minute():
    current_second = now()
    return current_second - (current_second % 60)


def last_full_day():
    current_second = now()
    return current_second - (current_second % SECONDS_IN_DAY)


def hours_passed_today():
    return (now() - last_full_day()) / SECONDS_IN_HOUR


def now_hrf() -> str:
    """Get current timestamp in human readable format."""
    return str(datetime.fromtimestamp(now()))


def add_query_params_to_url(url: str, query_params: Dict[str, str]) -> str:
    """Add query parameters to a URL."""
    req = PreparedRequest()
    req.prepare_url(url, query_params)
    return str(req.url)
