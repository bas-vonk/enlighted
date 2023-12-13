import datetime
import logging
from collections.abc import Generator
from time import sleep
from typing import Dict, Union

import redis
from requests import Response
from scheduler import Scheduler  # type: ignore
from sqlalchemy.orm import Session

from enlighted.db import AuthDbConfig, BronzeDbConfig, get_engine, get_session
from enlighted.oauth2.models import AccessToken, RefreshToken
from enlighted.oauth2.nibe.oauth2 import (NibeAuthorizationCodeGrant,
                                          NibeRefreshTokenGrant)
from enlighted.pipelines.api2bronze.base_etl import BaseETL
from enlighted.pipelines.api2bronze.nibe.config import (NibeSettings,
                                                        ParameterList)
from enlighted.pipelines.api2bronze.nibe.models import Base, Data
from enlighted.utils import last_full_minute, now_hrf

settings = NibeSettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Nibe ETL")

# https://hvacrschool.com/wp-content/uploads/2017/08/img_7948-1.jpg
# https://www.openhab.org/addons/bindings/nibeheatpump/
# https://github.com/anerdins/nibepi/blob/master/docker/nibepi/models/F1255.json
# https://www.nibe.eu/assets/documents/19781/231538-5.pdf
# https://www.nibe.eu/download/18.776ca07716c43fb658831b/1565862120037/omschakeling_koelen_verwarmen_1145_1245_1155_1255.pdf


class NibeSystemStatusETL(BaseETL):
    def __init__(self, session: Session):
        self.session = session
        self.api_request_resource_url = (
            f"{settings.api_base_url}/api/v1/systems/{settings.system_id}/status/system"
        )

        BaseETL.__init__(
            self,
            session=self.session,
            etl_run_start_time=last_full_minute(),
            is_stream=False,
            access_token=None,
            refresh_token_grant=NibeRefreshTokenGrant(self.session),
            authorization_code_grant=NibeAuthorizationCodeGrant(self.session),
        )

    def transform(
        self, response: Response
    ) -> Generator[Dict[str, Union[str, int, float]], None, None]:
        """Transform the response."""

        icons_active = [icon["image"]["name"] for icon in response.json()]

        if "Heating" in icons_active:
            display_value = "heating"
        elif "Drop" in icons_active:
            display_value = "hot_water"
        elif "Cooling" in icons_active:
            display_value = "cooling"
        else:
            display_value = "inactive"

        yield {
            "parameterId": 1000,
            "title": "System status",
            "created": self.etl_run_start_time,
            "displayValue": display_value,
            "unit": "",
            "designation": "EP14",
        }

    def load(self, row: Dict[str, Union[str, int, float]]) -> None:
        data = Data.upsert(self.session, row)
        redis_obj = redis.Redis(host="192.168.2.202", port=6379, decode_responses=True)
        redis_obj.lpush("nibe.Data", data.id)

    def run(self) -> None:
        """Run the pipeline."""

        # Add sleep to respect the rate limits: https://api.nibeuplink.com/docs/v1
        sleep(4)

        self.do_job(self.api_request_resource_url, None)

        logger.info(f"Run for SystemStatusETL completed at {now_hrf()}")


class NibeParametersETL(BaseETL):
    def __init__(self, session: Session):
        self.session = session
        self.api_request_resource_url = (
            f"{settings.api_base_url}/api/v1/systems/{settings.system_id}/parameters"
        )

        BaseETL.__init__(
            self,
            session=self.session,
            etl_run_start_time=last_full_minute(),
            is_stream=False,
            access_token=None,
            refresh_token_grant=NibeRefreshTokenGrant(self.session),
            authorization_code_grant=NibeAuthorizationCodeGrant(self.session),
        )

    def transform(
        self, response: Response
    ) -> Generator[Dict[str, Union[str, int, float]], None, None]:
        for observation in response.json():
            yield {
                "parameterId": observation["parameterId"],
                "title": observation["title"],
                "created": self.etl_run_start_time,
                "displayValue": observation["displayValue"],
                "unit": observation["unit"],
                "designation": observation["designation"],
            }

    def load(self, row: Dict[str, Union[str, int, float]]) -> None:
        data = Data.upsert(self.session, row)
        redis_obj = redis.Redis(host="192.168.2.202", port=6379, decode_responses=True)
        redis_obj.lpush("nibe.Data", data.id)

    def run(self, parameters: ParameterList) -> None:
        # Nibe API accepts 15 parameter ids per request, so chunk all the parameters
        # that we want to get
        parameter_ids = [parameter["parameter_id"] for parameter in parameters]
        for parameter_ids in [
            parameter_ids[i : i + settings.max_params_per_call]
            for i in range(0, len(parameter_ids), settings.max_params_per_call)
        ]:
            # Add sleep to respect the rate limits: https://api.nibeuplink.com/docs/v1
            sleep(4)

            # For each loop here, run the entire ETL (starting at extract)
            # Per loop, new request parameters need to be added
            self.do_job(self.api_request_resource_url, {"parameterIds": parameter_ids})

        logger.info(f"Run for ParametersETL completed at {now_hrf()}")


if __name__ == "__main__":
    engine = get_engine(BronzeDbConfig())
    session = get_session(
        {
            AccessToken: AuthDbConfig(),
            RefreshToken: AuthDbConfig(),
            Data: BronzeDbConfig(),
        }
    )

    """Create all tables."""
    Base.metadata.create_all(engine)

    # Create the scheduler
    schedule = Scheduler()
    schedule.minutely(
        datetime.time(second=1),
        lambda: NibeParametersETL(session).run(settings.parameters_each_minute),
    )
    schedule.hourly(
        datetime.time(minute=0, second=1),
        lambda: NibeParametersETL(session).run(settings.parameters_each_hour),
    )
    schedule.minutely(
        datetime.time(second=1),
        lambda: NibeSystemStatusETL(session).run(),
    )

    while True:
        schedule.exec_jobs()
        sleep(0.1)
