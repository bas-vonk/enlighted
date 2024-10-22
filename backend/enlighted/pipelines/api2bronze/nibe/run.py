import datetime
import logging
from collections.abc import Generator
from time import sleep
from typing import Dict, Union

import redis
from enlighted.db import AuthDbConfig, BronzeDbConfig, get_engine, get_session
from enlighted.oauth2.models import AccessToken
from enlighted.oauth2.nibe.oauth2 import NibeClientCredentialsGrant
from enlighted.pipelines.api2bronze.a2b_etl import BaseApi2BronzeETL
from enlighted.pipelines.api2bronze.nibe.config import NibeSettings
from enlighted.pipelines.api2bronze.nibe.models import Base, Data
from enlighted.utils import last_full_minute, now_hrf
from redis import Redis
from requests import Response
from scheduler import Scheduler  # type: ignore
from sqlalchemy.orm import Session

settings = NibeSettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Nibe ETL")

# https://hvacrschool.com/wp-content/uploads/2017/08/img_7948-1.jpg
# https://www.openhab.org/addons/bindings/nibeheatpump/
# https://github.com/anerdins/nibepi/blob/master/docker/nibepi/models/F1255.json
# https://www.nibe.eu/assets/documents/19781/231538-5.pdf
# https://www.nibe.eu/download/18.776ca07716c43fb658831b/1565862120037/omschakeling_koelen_verwarmen_1145_1245_1155_1255.pdf


class NibeETL(BaseApi2BronzeETL):
    def __init__(self, session: Session, redis_obj: redis):
        self.session = session
        self.redis_obj = redis_obj
        self.api_request_resource_url = (
            f"{settings.api_base_url}/v2/devices/{settings.device_id}/points"
        )

        BaseApi2BronzeETL.__init__(
            self,
            session=self.session,
            etl_run_start_time=last_full_minute(),
            is_stream=False,
            access_token=None,
            client_credentials_grant=NibeClientCredentialsGrant(
                self.session, settings.api_token_url
            ),
        )

    def transform(
        self, response: Response
    ) -> Generator[Dict[str, Union[str, int, float]], None, None]:

        for observation in response.json():
            yield {
                "parameterId": observation["parameterId"],
                "parameterName": observation["parameterName"],
                "parameterUnit": observation["parameterUnit"],
                "value": observation["value"],
                "strVal": observation["strVal"],
                "timestamp": observation["timestamp"],
                "created": self.etl_run_start_time,
            }

    def load(self, row: Dict[str, Union[str, int, float]]) -> None:
        data = Data.upsert(self.session, row)
        self.redis_obj.lpush("nibe.Data", data.id)

    def run(self) -> None:

        self.do_job(self.api_request_resource_url)
        logger.info(f"Run for Api2Bronze ETL completed at {now_hrf()}")


if __name__ == "__main__":
    # Databases
    engine = get_engine(BronzeDbConfig())
    session = get_session(
        {
            AccessToken: AuthDbConfig(),
            Data: BronzeDbConfig(),
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
        lambda: NibeETL(session=session, redis_obj=redis_obj).run(),
    )

    while True:
        schedule.exec_jobs()
        sleep(0.1)
