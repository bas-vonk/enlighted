from typing import Dict

from pydantic_settings import BaseSettings


class HomeConnectSettings(BaseSettings):
    client_id: str
    client_secret: str
    scope: str = (
        "IdentifyAppliance Oven-Monitor Dishwasher-Monitor FridgeFreezer-Monitor"
    )
    state: str = "STATE"
    redirect_uri: str

    api_base_url: str = "https://api.home-connect.com"
    api_token_url: str = api_base_url + "/security/oauth/token"
    api_authorization_code_url: str = api_base_url + "/security/oauth/authorize"

    home_appliance_ids: Dict[str, str] = {
        "SIEMENS-HM876G0B6-68A40E8DFAFD": "oven",
        "012090386871006546": "dishwasher",
    }

    db_username: str
    db_password: str
    db_hostname: str
    db_database: str
    db_port: str
