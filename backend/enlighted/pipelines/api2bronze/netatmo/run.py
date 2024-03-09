import datetime
import logging
from collections import defaultdict
from collections.abc import Generator
from pprint import pprint
from time import sleep
from typing import Dict, Union

import redis
from numpy import mean
from redis import Redis
from requests import Response
from scheduler import Scheduler  # type: ignore
from sqlalchemy.orm import Session

from enlighted.db import AuthDbConfig, BronzeDbConfig, get_engine, get_session
from enlighted.oauth2.models import AccessToken, RefreshToken
from enlighted.oauth2.netatmo.oauth2 import (
    NetatmoAuthorizationCodeGrant,
    NetatmoRefreshTokenGrant,
)
from enlighted.pipelines.api2bronze.a2b_etl import BaseApi2BronzeETL
from enlighted.pipelines.api2bronze.netatmo.config import NetatmoSettings
from enlighted.pipelines.api2bronze.netatmo.models import (
    Base,
    IndoorMeasurement,
    OutdoorMeasurement,
)
from enlighted.utils import last_full_minute, now, now_hrf

settings = NetatmoSettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Netatmo ETL")


class NetatmoIndoorETL(BaseApi2BronzeETL):
    def __init__(self, session: Session, redis_obj: redis):
        self.session = session
        self.redis_obj = redis_obj
        self.api_request_resource_url = settings.urls["indoor"]

        BaseApi2BronzeETL.__init__(
            self,
            session=self.session,
            etl_run_start_time=now(),
            is_stream=False,
            access_token=None,
            refresh_token_grant=NetatmoRefreshTokenGrant(self.session),
            authorization_code_grant=NetatmoAuthorizationCodeGrant(self.session),
        )

    def transform(
        self, response: Response
    ) -> Generator[Dict[str, Union[str, int, float]], None, None]:
        main_module = response.json()["body"]["home"]["modules"][0]

        for parameter_name in settings.indoor_parameter_names:
            yield {
                "parameter_name": parameter_name,
                "ts": main_module["ts"],
                "value": main_module[parameter_name],
                "unit": settings.units[parameter_name],
            }

    def load(self, row: Dict[str, Union[str, int, float]]) -> None:
        measurement = IndoorMeasurement.upsert(self.session, row)
        self.redis_obj.lpush("netatmo.IndoorMeasurement", measurement.id)

    def run(self) -> None:
        self.do_job(self.api_request_resource_url, settings.indoor_query_parameters)
        logger.info(f"Run for Netatmo Indoor ETL completed at {now_hrf()}")


class NetatmoOutdoorETL(BaseApi2BronzeETL):
    def __init__(self, session: Session, redis_obj: redis):
        self.session = session
        self.redis_obj = redis_obj
        self.api_request_resource_url = settings.urls["outdoor"]

        BaseApi2BronzeETL.__init__(
            self,
            session=self.session,
            etl_run_start_time=last_full_minute(),
            is_stream=False,
            access_token=None,
            refresh_token_grant=NetatmoRefreshTokenGrant(self.session),
            authorization_code_grant=NetatmoAuthorizationCodeGrant(self.session),
        )

    def transform(
        self, response: Response
    ) -> Generator[Dict[str, Union[str, int, float]], None, None]:
        houses = [
            dict(zip(measurements["type"], list(measurements["res"].values())[0]))
            if "res" in measurements and "type" in measurements
            else measurements
            for house in response.json()["body"]
            for device_mac, measurements in house["measures"].items()
        ]

        measurements_values = defaultdict(lambda: [])
        for measurements_dict in houses:
            for parameter_name, value in measurements_dict.items():
                measurements_values[parameter_name].append(value)

        ts = now()
        for parameter_name, values in measurements_values.items():
            if parameter_name in ["rain_timeutc", "wind_timeutc"]:
                continue

            yield {
                "parameter_name": parameter_name,
                "ts": ts,
                "value": mean(values),
                "unit": settings.units[parameter_name],
                "amount_of_stations": len(values),
            }

    def load(self, row: Dict[str, Union[str, int, float]]) -> None:
        measurement = OutdoorMeasurement.upsert(self.session, row)
        self.redis_obj.lpush("netatmo.OutdoorMeasurement", measurement.id)

    def run(self) -> None:
        self.do_job(self.api_request_resource_url, settings.outdoor_query_parameters)
        logger.info(f"Run for Netatmo Outdoor ETL completed at {now_hrf()}")


if __name__ == "__main__":
    # Databases
    engine = get_engine(BronzeDbConfig())
    session = get_session(
        {
            AccessToken: AuthDbConfig(),
            RefreshToken: AuthDbConfig(),
            IndoorMeasurement: BronzeDbConfig(),
            OutdoorMeasurement: BronzeDbConfig(),
        }
    )

    # Redis
    redis_obj = redis.Redis(host="192.168.2.201", port=6379, decode_responses=True)

    """Ensure all tables exist."""
    Base.metadata.create_all(engine)

    # Create the scheduler
    schedule = Scheduler()

    schedule.minutely(
        datetime.time(second=0),
        lambda: NetatmoIndoorETL(session=session, redis_obj=redis_obj).run(),
    )
    schedule.cyclic(
        datetime.timedelta(minutes=10),
        lambda: NetatmoOutdoorETL(session=session, redis_obj=redis_obj).run(),
    )

    while True:
        schedule.exec_jobs()
        sleep(0.1)
