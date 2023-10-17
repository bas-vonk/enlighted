import argparse
import json
import logging
from collections.abc import Generator
from time import sleep
from typing import Any, Dict, Union

import sseclient
from requests import Response
from requests.exceptions import ChunkedEncodingError
from sqlalchemy.engine import Engine
from urllib3.exceptions import InvalidChunkLength, ProtocolError

from minimal_footprint.db import create_all_tables, get_engine
from minimal_footprint.etl import ETL
from minimal_footprint.integrations.homeconnect.config import HomeConnectSettings
from minimal_footprint.integrations.homeconnect.models import Base, OperationState
from minimal_footprint.integrations.homeconnect.oauth2 import (
    HomeConnectAuthorizationCodeGrant,
    HomeConnectRefreshTokenGrant,
)
from minimal_footprint.utils import now, now_hrf

settings = HomeConnectSettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HomeConnect ETL")


def transform(
    response: Generator[bytes, None, None], _: Any
) -> Generator[Dict[str, Union[str, int]], None, None]:
    # When something happens with the message stream, stop the iteration
    try:
        client = sseclient.SSEClient(response)
        for event in client.events():
            try:
                message = json.loads(event.data)
                for item in message["items"]:
                    # Only store the OperationState messages
                    if item["key"] != "BSH.Common.Status.OperationState":
                        logger.info(f"Ignored message received at {now_hrf()}")
                        continue

                    yield {
                        "appliance_name": settings.home_appliance_ids[message["haId"]],
                        "datetime_stored": item["timestamp"],
                        "state": item["value"],
                    }
                    logger.info(f"OperationState message received at {now_hrf()}.")

            except json.decoder.JSONDecodeError:
                logger.info(f"Empty message received at {now_hrf()}.")
    except (ChunkedEncodingError, InvalidChunkLength, ProtocolError, KeyError):
        logger.warning(f"Message stream interrupted at {now_hrf()}.")
        return  # According to PEP479: https://peps.python.org/pep-0479/


def job(engine: Engine, ha_id: str) -> None:
    """Run the ETL."""

    # We want timestamp to be the same for the entire run
    start_run_timestamp = now()

    # Nibe API accepts 15 parameter ids per request, so chunk all the parameters
    # that we want to get
    homeconnect_etl = ETL(
        engine=engine,
        target_table=OperationState,
        api_resource_url=f"{settings.api_base_url}/api/homeappliances/{ha_id}/events",
        api_request_query_params=None,
        etl_run_start_time=start_run_timestamp,
        transform_function=transform,
        is_stream=True,
        access_token=None,
        refresh_token_grant=HomeConnectRefreshTokenGrant(engine),
        authorization_code_grant=HomeConnectAuthorizationCodeGrant(engine),
    )
    homeconnect_etl.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ha_id")
    args = parser.parse_args()

    engine = get_engine(settings)
    create_all_tables(Base, engine)

    while True:
        job(engine, args.ha_id)
        logger.info(f"Still running at {now_hrf()}")
        sleep(settings.sleep_between_runs_seconds)
