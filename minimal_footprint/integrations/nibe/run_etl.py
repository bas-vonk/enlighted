import logging
from collections.abc import Generator
from time import sleep
from typing import Dict, Union

from requests import Response
from sqlalchemy.engine import Engine

from minimal_footprint.db import get_engine
from minimal_footprint.etl import BaseETL
from minimal_footprint.integrations.nibe.config import NibeSettings
from minimal_footprint.integrations.nibe.models import Base, Data
from minimal_footprint.integrations.nibe.oauth2 import NibeRefreshTokenGrant
from minimal_footprint.utils import now, now_hrf

settings = NibeSettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Nibe ETL")

# https://hvacrschool.com/wp-content/uploads/2017/08/img_7948-1.jpg
# https://www.openhab.org/addons/bindings/nibeheatpump/
# https://github.com/anerdins/nibepi/blob/master/docker/nibepi/models/F1255.json
# https://www.nibe.eu/assets/documents/19781/231538-5.pdf
# https://www.nibe.eu/download/18.776ca07716c43fb658831b/1565862120037/omschakeling_koelen_verwarmen_1145_1245_1155_1255.pdf


class NibeETL(BaseETL):
    def __init__(self, engine: Engine):
        self.engine = engine
        self.api_request_resource_url = (
            f"{settings.api_base_url}/api/v1/systems/{settings.system_id}/parameters"
        )

        BaseETL.__init__(
            self,
            engine=self.engine,
            etl_run_start_time=now(),
            is_stream=False,
            access_token=None,
            refresh_token_grant=NibeRefreshTokenGrant(self.engine),
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

    def run(self) -> None:
        # Nibe API accepts 15 parameter ids per request, so chunk all the parameters
        # that we want to get
        for parameter_ids in [
            settings.parameter_ids[i : i + settings.max_params_per_call]
            for i in range(0, len(settings.parameter_ids), settings.max_params_per_call)
        ]:
            # For each loop here, run the entire ETL (starting at extract)
            # Per loop, new request parameters need to be added
            self.do_job(self.api_request_resource_url, {"parameterIds": parameter_ids})


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

    while True:
        nibe_etl = NibeETL(engine)
        nibe_etl.run()

        logger.info(f"Still running at {now_hrf()}")
        sleep(settings.sleep_between_runs_seconds)
