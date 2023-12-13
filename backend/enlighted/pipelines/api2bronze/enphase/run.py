import datetime
import logging
from collections.abc import Generator
from time import sleep
from typing import Dict, Union

import redis
from enlighted.db import BronzeDbConfig, get_engine, get_session
from enlighted.pipelines.api2bronze.base_etl import BaseETL
from enlighted.pipelines.api2bronze.enphase.config import EnphaseSettings
from enlighted.pipelines.api2bronze.enphase.models import Base, Production
from enlighted.utils import now, now_hrf
from requests import Response
from scheduler import Scheduler  # type: ignore
from sqlalchemy.orm import Session

settings = EnphaseSettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Enphase ETL")


class EnphaseEnvoyETL(BaseETL):
    def __init__(self, session: Session):
        self.session = session

        BaseETL.__init__(
            self,
            session=self.session,
            etl_run_start_time=now(),
            is_stream=False,
            access_token=settings.api_token,
            verify_ssl=False,
        )

    def transform(
        self, response: Response
    ) -> Generator[Dict[str, Union[str, int, float]], None, None]:
        yield {
            "readingTime": response.json()["production"][0]["readingTime"],
            "wNow": response.json()["production"][0]["wNow"],
            "activeCount": response.json()["production"][0]["activeCount"],
        }

        return

    def load(self, row: Dict[str, Union[str, int, float]]) -> None:
        production = Production.upsert(self.session, row)
        redis_obj = redis.Redis(host="192.168.2.202", port=6379, decode_responses=True)
        redis_obj.lpush("enphase.Production", production.id)

    def run(self) -> None:
        """Run the ETL."""
        self.do_job(f"{settings.api_url}/production.json", None)
        logger.info(f"Run completed at {now_hrf()}")


if __name__ == "__main__":
    engine = get_engine(BronzeDbConfig())
    session = get_session(
        {
            Production: BronzeDbConfig(),
        }
    )

    """Create all tables."""
    Base.metadata.create_all(engine)

    schedule = Scheduler()
    schedule.minutely(datetime.time(second=0), lambda: EnphaseEnvoyETL(session).run())

    while True:
        schedule.exec_jobs()
        sleep(1)
