import logging
from collections.abc import Generator
from time import sleep
from typing import Dict, Union

from requests import Response
from sqlalchemy.engine import Engine

from minimal_footprint.db import get_engine
from minimal_footprint.etl import BaseETL
from minimal_footprint.integrations.tibber.config import TibberSettings
from minimal_footprint.integrations.tibber.models import Base, Consumption, Production
from minimal_footprint.utils import now, now_hrf, ts_str_to_unix

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Tibber ETL")

settings = TibberSettings()


class TibberETL(BaseETL):
    def __init__(self, engine: Engine):
        self.engine = engine
        self.api_request_resource_url = settings.api_url

        BaseETL.__init__(
            self,
            engine=self.engine,
            etl_run_start_time=now(),
            is_stream=False,
            access_token=settings.api_token,
            refresh_token_grant=None,
        )


class ConsumptionTibberETL(TibberETL):
    def __init__(self, engine: Engine):
        TibberETL.__init__(self, engine)

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
            yield {
                "period_start": ts_str_to_unix(node["from"], settings.api_ts_str_fmt),
                "period_end": ts_str_to_unix(node["to"], settings.api_ts_str_fmt),
                "unit_price": node["unitPrice"],
                "cost": node["cost"],
                "consumption": node["consumption"],
                "consumption_unit": node["consumptionUnit"],
            }

    def load(self, row: Dict[str, Union[str, int, float]]) -> None:
        Consumption.upsert(self.engine, row)

    def run(self) -> None:
        self.do_job(settings.api_url, self.api_request_query_params)


class ProductionTibberETL(TibberETL):
    def __init__(self, engine: Engine):
        TibberETL.__init__(self, engine)

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
            yield {
                "period_start": ts_str_to_unix(node["from"], settings.api_ts_str_fmt),
                "period_end": ts_str_to_unix(node["to"], settings.api_ts_str_fmt),
                "unit_price": node["unitPrice"],
                "revenue": node["profit"],
                "production": node["production"],
                "production_unit": node["productionUnit"],
            }

    def load(self, row: Dict[str, Union[str, int, float]]) -> None:
        Production.upsert(self.engine, row)

    def run(self) -> None:
        self.do_job(settings.api_url, self.api_request_query_params)


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
        ConsumptionTibberETL(engine).run()
        ProductionTibberETL(engine).run()
        logger.info(f"Still running at {now_hrf()}")
        sleep(settings.sleep_between_runs_seconds)
