from pydantic_settings import BaseSettings


class NetatmoSettings(BaseSettings):
    client_id: str
    client_secret: str
    scope: str = "read_station"
    state: str = "STATE"
    redirect_uri: str

    api_base_url: str = "https://api.netatmo.com"
    api_token_url: str = api_base_url + "/oauth2/token"
    api_authorization_code_url: str = api_base_url + "/oauth2/authorize"
