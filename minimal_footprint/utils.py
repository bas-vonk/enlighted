from datetime import datetime
from time import mktime, time

from requests.models import PreparedRequest


def ts_str_to_unix(timestamp_str: str, timestamp_str_format: str) -> int:
    """Convert a datetime string to unix timestamp."""
    return int(
        mktime(datetime.strptime(timestamp_str, timestamp_str_format).timetuple())
    )


def now() -> int:
    """Get current timestamp in unix."""
    return int(time())


def now_hrf() -> str:
    """Get current timestamp in human readable format."""
    return str(datetime.fromtimestamp(now()))


def add_query_params_to_url(url: str, query_params: dict) -> str:
    """Add query parameters to a URL."""
    req = PreparedRequest()
    req.prepare_url(url, query_params)
    return str(req.url)
