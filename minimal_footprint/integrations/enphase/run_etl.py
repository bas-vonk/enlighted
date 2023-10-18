import logging
from collections import defaultdict
from collections.abc import Generator
from time import sleep
from typing import Dict, Union

from requests import Response
from sqlalchemy.engine import Engine

from minimal_footprint.db import get_engine
from minimal_footprint.etl import BaseETL
from minimal_footprint.integrations.enphase.config import EnphaseSettings
from minimal_footprint.integrations.enphase.models import Base, Production
from minimal_footprint.integrations.enphase.oauth2 import EnphaseRefreshTokenGrant
from minimal_footprint.utils import now, now_hrf

settings = EnphaseSettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Enphase ETL")

SECONDS_IN_HOUR = 3600
LOOKBACK_IN_HOURS = 12


class EnphaseETL(BaseETL):
    def __init__(self, engine: Engine):
        self.engine = engine

        BaseETL.__init__(
            self,
            engine=self.engine,
            etl_run_start_time=now(),
            is_stream=False,
            access_token=None,
            refresh_token_grant=EnphaseRefreshTokenGrant(self.engine),
        )

    def transform(
        self, response: Response
    ) -> Generator[Dict[str, Union[str, int, float]], None, None]:
        values_per_interval_start = defaultdict(lambda: [])
        for interval in response.json()["intervals"]:
            hour_for_period = interval["end_at"] - interval["end_at"] % SECONDS_IN_HOUR
            interval_start = (
                hour_for_period
                if interval["end_at"] != hour_for_period
                else hour_for_period - SECONDS_IN_HOUR
            )
            values_per_interval_start[interval_start].append(interval["enwh"])

        for interval_start, values in values_per_interval_start.items():
            yield {
                "period_start": interval_start,
                "period_end": interval_start + SECONDS_IN_HOUR,
                "watt_hours": sum(values),
            }

        return

    def load(self, row: Dict[str, Union[str, int, float]]) -> None:
        Production.upsert(self.engine, row)

    def run(self) -> None:
        """Run the ETL."""

        # Get the last full hour and the start hour
        end_at = self.etl_run_start_time - (self.etl_run_start_time % SECONDS_IN_HOUR)
        start_at = end_at - (LOOKBACK_IN_HOURS * SECONDS_IN_HOUR)

        api_request_query_params = {
            "start_at": start_at,
            "end_at": end_at,
            "granularity": "day",
            "key": settings.api_key,
        }

        self.do_job(
            f"{settings.api_base_url}/api/v4/systems/{settings.system_id}"
            f"/telemetry/production_micro",
            api_request_query_params,
        )


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
        enphase_etl = EnphaseETL(engine)
        enphase_etl.run()

        logger.info(f"Still running at {now_hrf()}")
        sleep(settings.sleep_between_runs_seconds)
