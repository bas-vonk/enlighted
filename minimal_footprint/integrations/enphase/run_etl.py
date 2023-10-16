import logging
from collections import defaultdict
from time import sleep

from minimal_footprint.db import create_all_tables, get_engine
from minimal_footprint.etl import ETL
from minimal_footprint.integrations.enphase.config import EnphaseSettings
from minimal_footprint.integrations.enphase.models import Base, Production
from minimal_footprint.integrations.enphase.oauth2 import (
    EnphaseAuthorizationCodeGrant,
    EnphaseRefreshTokenGrant,
)
from minimal_footprint.utils import now, now_hrf

settings = EnphaseSettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Enphase ETL")

SECONDS_IN_HOUR = 3600
LOOKBACK_IN_HOURS = 12


def transform(response_body: dict, _):
    values_per_interval_start = defaultdict(lambda: [])
    for interval in response_body["intervals"]:
        hour_for_period = interval["end_at"] - interval["end_at"] % SECONDS_IN_HOUR
        interval_start = (
            hour_for_period
            if interval["end_at"] != hour_for_period
            else hour_for_period - SECONDS_IN_HOUR
        )
        values_per_interval_start[interval_start].append(interval["enwh"])

    rows = []
    for interval_start, values in values_per_interval_start.items():
        rows.append(
            {
                "period_start": interval_start,
                "period_end": interval_start + SECONDS_IN_HOUR,
                "watt_hours": sum(values),
            }
        )
    return rows


def job(engine):
    """Run the ETL."""

    # We want timestamp to be the same for the entire run
    start_run_timestamp = now()

    # Get the last full hour and the start hour
    end_at = start_run_timestamp - (start_run_timestamp % SECONDS_IN_HOUR)
    start_at = end_at - (LOOKBACK_IN_HOURS * SECONDS_IN_HOUR)

    api_request_query_params = {
        "start_at": start_at,
        "end_at": end_at,
        "granularity": "day",
        "key": settings.api_key,
    }

    enphase_etl = ETL(
        engine=engine,
        target_table=Production,
        api_resource_url=f"{settings.api_base_url}/api/v4/systems/{settings.system_id}/telemetry/production_micro",
        api_request_query_params=api_request_query_params,
        etl_run_start_time=start_run_timestamp,
        transform_function=transform,
        is_stream=False,
        access_token=None,
        refresh_token_grant=EnphaseRefreshTokenGrant(engine),
        authorization_code_grant=EnphaseAuthorizationCodeGrant(engine),
    )
    enphase_etl.run()


if __name__ == "__main__":
    engine = get_engine(settings)
    create_all_tables(Base, engine)

    while True:
        job(engine)
        logger.info(f"Still running at {now_hrf()}")
        sleep(settings.sleep_between_runs_seconds)
