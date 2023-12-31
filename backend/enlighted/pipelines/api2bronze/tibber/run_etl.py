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
from enlighted.pipelines.api2bronze.tibber.config import TibberSettings
from enlighted.pipelines.api2bronze.tibber.models import Base, Consumption, Production
from enlighted.utils import now, now_hrf, ts_str_to_unix

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Tibber ETL")

settings = TibberSettings()


class TibberETL(BaseApi2BronzeETL):
    def __init__(self, session: Session):
        self.session = session
        self.api_request_resource_url = settings.api_url

        BaseApi2BronzeETL.__init__(
            self,
            session=self.session,
            etl_run_start_time=now(),
            is_stream=False,
            access_token=settings.api_token,
            refresh_token_grant=None,
        )


class ConsumptionTibberETL(TibberETL):
    def __init__(self, session: Session, redis_obj: Redis):
        self.redis_obj = redis_obj
        TibberETL.__init__(self, session)

    @property
    def api_request_query_params(self) -> Dict[str, str]:
        """Get the JSON body for the consumption request."""
        query = """
        {
            viewer {
                homes {
                    consumption(resolution: HOURLY, last: 48) {
                        nodes {
                            from
                            to
                            cost
                            unitPrice
                            unitPriceVAT
                            consumption
                            consumptionUnit
                        }
                    }
                }
            }
        }
        """
        return {"query": query}

    def transform(
        self, response: Response
    ) -> Generator[Dict[str, Union[int, float, str]], None, None]:
        for node in response.json()["data"]["viewer"]["homes"][0]["consumption"][
            "nodes"
        ]:
            node["From"] = ts_str_to_unix(node["from"], settings.api_ts_str_fmt)
            node["To"] = ts_str_to_unix(node["to"], settings.api_ts_str_fmt)
            del node["from"]
            del node["to"]

            yield node

    def load(self, row: Dict[str, Union[str, int, float]]) -> None:
        consumption = Consumption.upsert(self.session, row)
        self.redis_obj.lpush("tibber.Consumption", consumption.id)

    def run(self) -> None:
        self.do_job(settings.api_url, self.api_request_query_params)
        logger.info(f"Run completed at {now_hrf()} for {self.__class__.__name__}")


class ProductionTibberETL(TibberETL):
    def __init__(self, session: Session, redis_obj: Redis):
        self.redis_obj = redis_obj
        TibberETL.__init__(self, session)

    @property
    def api_request_query_params(self) -> Dict[str, str]:
        """Get the JSON body for the production request."""
        query = """
        {
            viewer {
                homes {
                    production(resolution: HOURLY, last: 48) {
                        nodes {
                            from
                            to
                            profit
                            unitPrice
                            unitPriceVAT
                            production
                            productionUnit
                        }
                    }
                }
            }
        }
        """
        return {"query": query}

    def transform(
        self, response: Response
    ) -> Generator[Dict[str, Union[int, float, str]], None, None]:
        for node in response.json()["data"]["viewer"]["homes"][0]["production"][
            "nodes"
        ]:
            node["From"] = ts_str_to_unix(node["from"], settings.api_ts_str_fmt)
            node["To"] = ts_str_to_unix(node["to"], settings.api_ts_str_fmt)
            del node["from"]
            del node["to"]

            yield node

    def load(self, row: Dict[str, Union[str, int, float]]) -> None:
        production = Production.upsert(self.session, row)
        self.redis_obj.lpush("tibber.Production", production.id)

    def run(self) -> None:
        self.do_job(settings.api_url, self.api_request_query_params)
        logger.info(f"Run completed at {now_hrf()} for {self.__class__.__name__}")


if __name__ == "__main__":
    # Databases
    engine = get_engine(BronzeDbConfig())
    session = get_session({Consumption: BronzeDbConfig(), Production: BronzeDbConfig()})

    # Redis
    redis_obj = redis.Redis(host="192.168.2.202", port=6379, decode_responses=True)

    """Ensure all tables exist."""
    Base.metadata.create_all(engine)

    # Create the scheduler
    schedule = Scheduler()
    schedule.hourly(
        datetime.time(minute=30),
        lambda: ProductionTibberETL(session=session, redis_obj=redis_obj).run(),
    )
    schedule.hourly(
        datetime.time(minute=30),
        lambda: ConsumptionTibberETL(session=session, redis_obj=redis_obj).run(),
    )

    while True:
        schedule.exec_jobs()
        time.sleep(60)
