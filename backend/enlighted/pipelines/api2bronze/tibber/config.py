from pydantic_settings import BaseSettings


class TibberSettings(BaseSettings):
    api_url: str = "https://api.tibber.com/v1-beta/gql"
    api_token: str
    api_ts_str_fmt: str = "%Y-%m-%dT%H:%M:%S.%f%z"
