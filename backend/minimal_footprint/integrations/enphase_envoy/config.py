from pydantic_settings import BaseSettings


class EnphaseEnvoySettings(BaseSettings):
    api_url: str = "https://192.168.2.203"  # Local Enphase Envoy-S address
    api_token: str

    db_username: str
    db_password: str
    db_hostname: str
    db_database: str
    db_port: str
