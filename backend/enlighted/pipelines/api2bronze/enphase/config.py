from pydantic_settings import BaseSettings


class EnphaseSettings(BaseSettings):
    api_url: str = "https://192.168.2.203"  # Local Enphase Envoy-S address
    api_token: str
