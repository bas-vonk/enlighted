from pydantic_settings import BaseSettings


class NibeSettings(BaseSettings):
    client_id: str
    client_secret: str
    scope: str = "READSYSTEM"

    api_base_url: str = "https://api.myuplink.com"
    api_token_url: str = api_base_url + "/oauth/token"

    device_id: str
