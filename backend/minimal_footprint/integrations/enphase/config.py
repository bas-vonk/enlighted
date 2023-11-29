from pydantic_settings import BaseSettings


class EnphaseSettings(BaseSettings):
    client_id: str
    client_secret: str
    api_key: str
    redirect_uri: str
    state: str = "STATE"

    api_base_url: str = "https://api.enphaseenergy.com"
    api_token_url: str = api_base_url + "/oauth/token"
    api_authorization_code_url: str = api_base_url + "/oauth/authorize"

    sleep_between_runs_seconds: int = 60 * 60 * 6

    db_username: str
    db_password: str
    db_hostname: str
    db_database: str
    db_port: str

    system_id: int
