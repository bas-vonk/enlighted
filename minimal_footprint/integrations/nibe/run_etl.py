import logging
from time import sleep

from minimal_footprint.db import create_all_tables, get_engine
from minimal_footprint.etl import ETL
from minimal_footprint.integrations.nibe.config import NibeSettings
from minimal_footprint.integrations.nibe.models import Base, Data
from minimal_footprint.integrations.nibe.oauth2 import (
    NibeAuthorizationCodeGrant,
    NibeRefreshTokenGrant,
)
from minimal_footprint.utils import now, now_hrf

settings = NibeSettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Nibe ETL")

# https://hvacrschool.com/wp-content/uploads/2017/08/img_7948-1.jpg
# https://www.openhab.org/addons/bindings/nibeheatpump/
# https://github.com/anerdins/nibepi/blob/master/docker/nibepi/models/F1255.json
# https://www.nibe.eu/assets/documents/19781/231538-5.pdf
# https://www.nibe.eu/download/18.776ca07716c43fb658831b/1565862120037/omschakeling_koelen_verwarmen_1145_1245_1155_1255.pdf


def transform(response, timestamp_for_data):
    for observation in response.json():
        yield {
            "parameter_id": observation["parameterId"],
            "parameter_name": observation["title"],
            "datetime_stored": timestamp_for_data,
            "display_value": observation["displayValue"],
            "unit": observation["unit"],
            "designation": observation["designation"],
        }


def job(engine):
    """Run the ETL."""

    # We want timestamp to be the same for the entire run
    start_run_timestamp = now()

    # Nibe API accepts 15 parameter ids per request, so chunk all the parameters
    # that we want to get
    for parameter_ids in [
        settings.parameter_ids[i : i + settings.max_params_per_call]
        for i in range(0, len(settings.parameter_ids), settings.max_params_per_call)
    ]:
        nibe_etl = ETL(
            engine=engine,
            target_table=Data,
            api_resource_url=f"{settings.api_base_url}/api/v1/systems/{settings.system_id}/parameters",
            api_request_query_params={"parameterIds": parameter_ids},
            etl_run_start_time=start_run_timestamp,
            transform_function=transform,
            is_stream=False,
            access_token=None,
            refresh_token_grant=NibeRefreshTokenGrant(engine),
            authorization_code_grant=NibeAuthorizationCodeGrant(engine),
        )
        nibe_etl.run()
        sleep(4)


if __name__ == "__main__":
    engine = get_engine(settings)
    create_all_tables(Base, engine)

    while True:
        job(engine)
        logger.info(f"Still running at {now_hrf()}")
        sleep(settings.sleep_between_runs_seconds)
