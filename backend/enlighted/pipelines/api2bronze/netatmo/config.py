from typing import Dict, List

from pydantic_settings import BaseSettings


class NetatmoSettings(BaseSettings):
    client_id: str
    client_secret: str
    scope: str = "read_station"
    state: str = "STATE"
    redirect_uri: str

    api_base_url: str = "https://api.netatmo.com/api"
    api_token_url: str = api_base_url + "/security/oauth/token"
    api_authorization_code_url: str = api_base_url + "/security/oauth/authorize"

    urls: Dict[str, str] = {
        "indoor": f"{api_base_url}/homestatus",
        "outdoor": f"{api_base_url}/getpublicdata",
    }

    indoor_query_parameters: Dict[str, str] = {"home_id": "65900364098aefc5c2060d8c"}

    outdoor_query_parameters: Dict[str, str] = {
        "lat_ne": "52.319794",
        "lon_ne": "5.037423",
        "lat_sw": "52.319794",
        "lon_sw": "5.037423",
    }

    units: Dict[str, str] = {
        "temperature": "°C",
        "co2": "ppm",
        "humidity": "%",
        "pressure": "bar",
        "noise": "dB",
        "rain_60min": "mm",
        "rain_24h": "mm",
        "rain_live": "mm",
        "wind_strength": "kp/h",
        "wind_angle": "°",
        "gust_strength": "kp/h",
        "gust_angle": "°",
    }

    indoor_parameter_names: List[str] = [
        "temperature",
        "co2",
        "humidity",
        "noise",
        "pressure",
    ]
