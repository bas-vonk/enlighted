from datetime import datetime
from time import mktime, time

from requests.models import PreparedRequest


def ts_str_to_unix(timestamp_str, timestamp_str_format):
    """Convert a datetime string to unix timestamp."""
    return mktime(datetime.strptime(timestamp_str, timestamp_str_format).timetuple())


def now():
    """Get current timestamp in unix."""
    return int(time())


def now_hrf():
    """Get current timestamp in human readable format."""
    return datetime.fromtimestamp(now())


def add_query_params_to_url(url: str, query_params: dict):
    """Add query parameters to a URL."""
    req = PreparedRequest()
    req.prepare_url(url, query_params)
    return req.url
