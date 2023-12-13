import json
from typing import IO, Dict, List, Union

from pydantic_settings import BaseSettings
from typing_extensions import TypedDict

with open("/www/enlighted/pipelines/_mappings/F1255PCv2.json") as f:
    paramdict = json.load(f)

ParameterList = List[Dict[str, Union[int, str, Dict[str, int]]]]
ParameterDict = TypedDict(
    "ParameterDict",
    {
        "sensors": ParameterList,
        "settings": ParameterList,
        "system_values": ParameterList,
        "not_implemented": List[int],
        "not_used": List[int],
    },
)


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
    system_id: int

    params: ParameterDict = paramdict
    parameters_each_minute: ParameterList = params["sensors"] + params["system_values"]
    parameters_each_hour: ParameterList = params["settings"]
