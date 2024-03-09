import datetime
import logging
from collections.abc import Generator
from time import sleep
from typing import Dict, Union

import redis
from redis import Redis
from requests import Response
from scheduler import Scheduler  # type: ignore
from sqlalchemy.orm import Session

from enlighted.db import BronzeDbConfig, get_engine, get_session
from enlighted.pipelines.api2bronze.a2b_etl import BaseApi2BronzeETL
from enlighted.pipelines.api2bronze.homewizard.config import HomeWizardSettings
from enlighted.pipelines.api2bronze.homewizard.models import Base, Measurement
from enlighted.utils import last_full_minute, now, now_hrf

settings = HomeWizardSettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HomeWizard ETL")


class HomeWizardETL(BaseApi2BronzeETL):
    def __init__(
        self,
        session: Session,
        redis_obj: redis,
        api_request_resource_url: str,
        observation_name: str,
    ):
        self.session = session
        self.redis_obj = redis_obj
        self.api_request_resource_url = api_request_resource_url
        self.observation_name = observation_name

        BaseApi2BronzeETL.__init__(
            self,
            session=self.session,
            access_token="not_needed",
            etl_run_start_time=last_full_minute(),
            is_stream=False,
        )

    def transform(
        self, response: Response
    ) -> Generator[Dict[str, Union[str, int, float]], None, None]:
        yield {
            "observation_name": self.observation_name,
            "observed_at": last_full_minute(),
            "total_power_import_t1_kwh": response.json()["total_power_import_t1_kwh"],
            "total_power_export_t1_kwh": response.json()["total_power_export_t1_kwh"],
            "active_power_w": response.json()["active_power_w"],
            "active_power_l1_w": response.json()["active_power_l1_w"],
        }

    def load(self, row: Dict[str, Union[str, int, float]]) -> None:
        measurement = Measurement.upsert(self.session, row)
        self.redis_obj.lpush("homewizard.Measurement", measurement.id)

    def run(self) -> None:
        self.do_job(self.api_request_resource_url)
        logger.info(f"Run for HomeWizard ETL completed at {now_hrf()}")


if __name__ == "__main__":
    # Databases
    engine = get_engine(BronzeDbConfig())
    session = get_session(
        {
            Measurement: BronzeDbConfig(),
        }
    )

    # Redis
    redis_obj = redis.Redis(host="192.168.2.201", port=6379, decode_responses=True)

    """Ensure all tables exist."""
    Base.metadata.create_all(engine)

    # Create all HomeWizard ETL objects
    etl_objects = []
    for api_request_resource_url, observation_name in settings.devices.items():
        etl_object = HomeWizardETL(
            session=session,
            redis_obj=redis_obj,
            api_request_resource_url=api_request_resource_url,
            observation_name=observation_name,
        )
        etl_objects.append(etl_object)

    # Create the scheduler
    schedule = Scheduler()
    for etl_object in etl_objects:
        schedule.minutely(datetime.time(second=1), etl_object.run)

    while True:
        schedule.exec_jobs()
        sleep(0.1)
