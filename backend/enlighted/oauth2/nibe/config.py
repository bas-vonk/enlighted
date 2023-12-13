from pydantic_settings import BaseSettings


class NibeSettings(BaseSettings):
    client_id: str
    client_secret: str
    redirect_uri: str
    state: str = "STATE"
    scope: str = "READSYSTEM"

    api_base_url: str = "https://api.nibeuplink.com"
    api_token_url: str = api_base_url + "/oauth/token"
    api_authorization_code_url: str = api_base_url + "/oauth/authorize"
