import json

from pydantic_settings import BaseSettings

with open("/www/minimal_footprint/integrations/nibe/F1255PC.json") as f:
    parameter_dict = json.load(f)


class NibeSettings(BaseSettings):
    client_id: str
    client_secret: str
    redirect_uri: str
    state: str = "STATE"
    scope: str = "READSYSTEM"

    api_base_url: str = "https://api.nibeuplink.com"
    api_token_url: str = api_base_url + "/oauth/token"
    api_authorization_code_url: str = api_base_url + "/oauth/authorize"
    max_params_per_call: int = 15

    sleep_between_runs_seconds: int = 60

    system_id: int

    parameter_ids: list = [
        parameter["parameter_id"] for parameter in parameter_dict["parameters_active"]
    ]

    db_username: str
    db_password: str
    db_hostname: str
    db_database: str
    db_port: str
