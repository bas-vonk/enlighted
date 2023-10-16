import logging
from time import sleep

from minimal_footprint.db import create_all_tables, get_engine
from minimal_footprint.etl import ETL
from minimal_footprint.integrations.tibber.config import TibberSettings
from minimal_footprint.integrations.tibber.models import Base, Consumption, Production
from minimal_footprint.utils import now, now_hrf, ts_str_to_unix

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Tibber ETL")

settings = TibberSettings()


def get_api_request_query_params_consumption():
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


def get_api_request_query_params_production():
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


def transform_consumption(response, _):
    for node in response.json()["data"]["viewer"]["homes"][0]["consumption"]["nodes"]:
        yield {
            "period_start": ts_str_to_unix(node["from"], settings.api_ts_str_fmt),
            "period_end": ts_str_to_unix(node["to"], settings.api_ts_str_fmt),
            "unit_price": node["unitPrice"],
            "cost": node["cost"],
            "consumption": node["consumption"],
            "consumption_unit": node["consumptionUnit"],
        }


def transform_production(response, _):
    for node in response.json()["data"]["viewer"]["homes"][0]["production"]["nodes"]:
        yield {
            "period_start": ts_str_to_unix(node["from"], settings.api_ts_str_fmt),
            "period_end": ts_str_to_unix(node["to"], settings.api_ts_str_fmt),
            "unit_price": node["unitPrice"],
            "revenue": node["profit"],
            "production": node["production"],
            "production_unit": node["productionUnit"],
        }


def job(engine):
    """Run the ETL."""

    # We want timestamp to be the same for the entire run
    start_run_timestamp = now()

    etls = [
        {
            "transform_function": transform_consumption,
            "api_request_query_params": get_api_request_query_params_consumption(),
            "target_table": Consumption,
        },
        {
            "transform_function": transform_production,
            "api_request_query_params": get_api_request_query_params_production(),
            "target_table": Production,
        },
    ]

    # Nibe API accepts 15 parameter ids per request, so chunk all the parameters
    # that we want to get
    for etl in etls:
        tibber_etl = ETL(
            engine=engine,
            target_table=etl["target_table"],
            api_resource_url=settings.api_url,
            api_request_query_params=etl["api_request_query_params"],
            etl_run_start_time=start_run_timestamp,
            transform_function=etl["transform_function"],
            is_stream=False,
            access_token=settings.api_token,
            refresh_token_grant=None,
            authorization_code_grant=None,
        )
        tibber_etl.run()


if __name__ == "__main__":
    engine = get_engine(settings)
    create_all_tables(Base, engine)

    while True:
        job(engine)
        logger.info(f"Still running at {now_hrf()}")
        sleep(settings.sleep_between_runs_seconds)
