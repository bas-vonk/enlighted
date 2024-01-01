import datetime
import logging
import time
from collections.abc import Generator
from typing import Dict, Union

import redis
from redis import Redis
from requests import Response
from scheduler import Scheduler  # type: ignore
from sqlalchemy.orm import Session

from enlighted.db import BronzeDbConfig, get_engine, get_session
from enlighted.pipelines.api2bronze.a2b_etl import BaseApi2BronzeETL
from enlighted.pipelines.api2bronze.enphase.config import EnphaseSettings
from enlighted.pipelines.api2bronze.enphase.models import Base, Production
from enlighted.utils import now, now_hrf

settings = EnphaseSettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Enphase ETL")


class EnphaseEnvoyETL(BaseApi2BronzeETL):
    def __init__(self, session: Session, redis_obj: Redis):
        self.session = session
        self.redis_obj = redis_obj

        BaseApi2BronzeETL.__init__(
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
    # Databases
    engine = get_engine(BronzeDbConfig())
    session = get_session(
        {
            Production: BronzeDbConfig(),
        }
    )

    # Redis
    redis_obj = redis.Redis(host="192.168.2.202", port=6379, decode_responses=True)

    """Ensure all tables exist."""
    Base.metadata.create_all(engine)

    schedule = Scheduler()
    schedule.minutely(
        datetime.time(second=0),
        lambda: EnphaseEnvoyETL(session=session, redis_obj=redis_obj).run(),
    )

    while True:
        schedule.exec_jobs()
        time.sleep(1)
