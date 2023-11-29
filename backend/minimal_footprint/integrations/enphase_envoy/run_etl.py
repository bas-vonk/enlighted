import datetime
import logging
from collections.abc import Generator
from time import sleep
from typing import Dict, Union

from requests import Response
from scheduler import Scheduler  # type: ignore
from sqlalchemy.engine import Engine

from minimal_footprint.db import get_engine
from minimal_footprint.etl import BaseETL
from minimal_footprint.integrations.enphase_envoy.config import EnphaseEnvoySettings
from minimal_footprint.integrations.enphase_envoy.models import Base, Production
from minimal_footprint.utils import now, now_hrf

settings = EnphaseEnvoySettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Enphase Envoy ETL")


class EnphaseEnvoyETL(BaseETL):
    def __init__(self, engine: Engine):
        self.engine = engine

        BaseETL.__init__(
            self,
            engine=self.engine,
            etl_run_start_time=now(),
            is_stream=False,
            access_token=settings.api_token,
            verify_ssl=False,
        )

    def transform(
        self, response: Response
    ) -> Generator[Dict[str, Union[str, int, float]], None, None]:
        yield {
            "datetime": response.json()["production"][0]["readingTime"],
            "production_watt": response.json()["production"][0]["wNow"],
            "active_inverter_count": response.json()["production"][0]["activeCount"],
        }

        return

    def load(self, row: Dict[str, Union[str, int, float]]) -> None:
        Production.upsert(self.engine, row)

    def run(self) -> None:
        """Run the ETL."""
        self.do_job(f"{settings.api_url}/production.json", None)
        logger.info(f"Run completed at {now_hrf()}")


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

    schedule = Scheduler()
    schedule.minutely(datetime.time(second=0), lambda: EnphaseEnvoyETL(engine).run())

    while True:
        schedule.exec_jobs()
        sleep(60)
