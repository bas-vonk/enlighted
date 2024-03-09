from typing import Dict

from pydantic_settings import BaseSettings


class HomeWizardSettings(BaseSettings):
    devices: Dict[str, str] = {
        "http://192.168.2.6/api/v1/data": "heat_recovery_ventilation",
        "http://192.168.2.24/api/v1/data": "entertainment_station",
        "http://192.168.2.25/api/v1/data": "dryer",
        "http://192.168.2.28/api/v1/data": "washing_machine",
        "http://192.168.2.42/api/v1/data": "quooker",
        "http://192.168.2.43/api/v1/data": "bathroom_heater",
        "http://192.168.2.44/api/v1/data": "raspi_cluster",
        "http://192.168.2.45/api/v1/data": "stove_left",
        "http://192.168.2.46/api/v1/data": "stove_right",
        "http://192.168.2.49/api/v1/data": "oven",
        "http://192.168.2.50/api/v1/data": "dishwasher",
        "http://192.168.2.51/api/v1/data": "fridge_freezer",
    }
