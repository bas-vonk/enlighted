import datetime
import logging
from collections.abc import Generator
from time import sleep
from typing import Dict, List, Union

from requests import Response
from scheduler import Scheduler  # type: ignore
from sqlalchemy.engine import Engine

from minimal_footprint.db import get_engine
from minimal_footprint.etl import BaseETL
from minimal_footprint.integrations.nibe.config import NibeSettings, ParameterList
from minimal_footprint.integrations.nibe.models import Base, Data
from minimal_footprint.integrations.nibe.oauth2 import (
    NibeAuthorizationCodeGrant,
    NibeRefreshTokenGrant,
)
from minimal_footprint.utils import last_full_minute, now_hrf

settings = NibeSettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Nibe ETL")

# https://hvacrschool.com/wp-content/uploads/2017/08/img_7948-1.jpg
# https://www.openhab.org/addons/bindings/nibeheatpump/
# https://github.com/anerdins/nibepi/blob/master/docker/nibepi/models/F1255.json
# https://www.nibe.eu/assets/documents/19781/231538-5.pdf
# https://www.nibe.eu/download/18.776ca07716c43fb658831b/1565862120037/omschakeling_koelen_verwarmen_1145_1245_1155_1255.pdf


class NibeSystemStatusETL(BaseETL):
    def __init__(self, engine: Engine):
        self.engine = engine
        self.api_request_resource_url = (
            f"{settings.api_base_url}/api/v1/systems/{settings.system_id}/status/system"
        )

        BaseETL.__init__(
            self,
            engine=self.engine,
            etl_run_start_time=last_full_minute(),
            is_stream=False,
            access_token=None,
            refresh_token_grant=NibeRefreshTokenGrant(self.engine),
            authorization_code_grant=NibeAuthorizationCodeGrant(self.engine),
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
            "parameter_id": 1000,
            "parameter_name": "System status",
            "datetime_stored": self.etl_run_start_time,
            "display_value": display_value,
            "unit": "",
            "designation": "EP14",
        }

    def load(self, row: Dict[str, Union[str, int, float]]) -> None:
        Data.upsert(self.engine, row)

    def run(self) -> None:
        """Run the pipeline."""

        # Add sleep to respect the rate limits: https://api.nibeuplink.com/docs/v1
        sleep(4)

        self.do_job(self.api_request_resource_url, None)

        logger.info(f"Run for SystemStatusETL completed at {now_hrf()}")


class NibeParametersETL(BaseETL):
    def __init__(self, engine: Engine):
        self.engine = engine
        self.api_request_resource_url = (
            f"{settings.api_base_url}/api/v1/systems/{settings.system_id}/parameters"
        )

        BaseETL.__init__(
            self,
            engine=self.engine,
            etl_run_start_time=last_full_minute(),
            is_stream=False,
            access_token=None,
            refresh_token_grant=NibeRefreshTokenGrant(self.engine),
            authorization_code_grant=NibeAuthorizationCodeGrant(self.engine),
        )

    def transform(
        self, response: Response
    ) -> Generator[Dict[str, Union[str, int, float]], None, None]:
        for observation in response.json():
            yield {
                "parameter_id": observation["parameterId"],
                "parameter_name": observation["title"],
                "datetime_stored": self.etl_run_start_time,
                "display_value": observation["displayValue"],
                "unit": observation["unit"],
                "designation": observation["designation"],
            }

    def load(self, row: Dict[str, Union[str, int, float]]) -> None:
        Data.upsert(self.engine, row)

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
    # Get an engine
    engine = get_engine(
        settings.db_username,
        settings.db_password,
        settings.db_hostname,
        settings.db_database,
        settings.db_port,
    )

    """Create all tables."""
    Base.metadata.create_all(engine)

    # Create the scheduler
    schedule = Scheduler()
    schedule.minutely(
        datetime.time(second=1),
        lambda: NibeParametersETL(engine).run(settings.parameters_each_minute),
    )
    schedule.hourly(
        datetime.time(minute=0, second=1),
        lambda: NibeParametersETL(engine).run(settings.parameters_each_hour),
    )
    schedule.minutely(
        datetime.time(second=1), lambda: NibeSystemStatusETL(engine).run()
    )

    while True:
        schedule.exec_jobs()
        sleep(0.1)