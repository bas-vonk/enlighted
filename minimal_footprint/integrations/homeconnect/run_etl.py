import argparse
import json
import logging
from collections.abc import Generator
from time import sleep
from typing import Dict, Union

import sseclient
from requests import Response
from requests.exceptions import ChunkedEncodingError
from sqlalchemy.engine import Engine
from urllib3.exceptions import InvalidChunkLength, ProtocolError

from minimal_footprint.db import get_engine
from minimal_footprint.etl import BaseETL
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


class HomeConnectETL(BaseETL):
    def __init__(self, engine: Engine, ha_id: int):
        self.engine = engine
        self.ha_id = ha_id

        BaseETL.__init__(
            self,
            engine=self.engine,
            etl_run_start_time=now(),
            is_stream=True,
            access_token=None,
            refresh_token_grant=HomeConnectRefreshTokenGrant(self.engine),
            authorization_code_grant=HomeConnectAuthorizationCodeGrant(self.engine)
        )

    def transform(
        self, response: Response
    ) -> Generator[Dict[str, Union[str, int, float]], None, None]:
        # When something happens with the message stream, stop the iteration
        try:
            client = sseclient.SSEClient(response)  # type: ignore
            for event in client.events():
                try:
                    message = json.loads(event.data)
                    for item in message["items"]:
                        # Only store the OperationState messages
                        if item["key"] != "BSH.Common.Status.OperationState":
                            logger.info(f"Ignored message received at {now_hrf()}")
                            continue

                        yield {
                            "appliance_name": settings.home_appliance_ids[
                                message["haId"]
                            ],
                            "datetime_stored": item["timestamp"],
                            "state": item["value"],
                        }
                        logger.info(f"OperationState message received at {now_hrf()}.")

                except json.decoder.JSONDecodeError:
                    logger.info(f"Empty message received at {now_hrf()}.")
        except (ChunkedEncodingError, InvalidChunkLength, ProtocolError, KeyError):
            logger.warning(f"Message stream interrupted at {now_hrf()}.")
            return  # According to PEP479: https://peps.python.org/pep-0479/

    def load(self, row: Dict[str, Union[str, int, float]]) -> None:
        OperationState.upsert(self.engine, row)

    def run(self) -> None:
        """Run the ETL."""

        self.do_job(
            f"{settings.api_base_url}/api/homeappliances/{self.ha_id}/events", None
        )

        logger.info(f"Still running at {now_hrf()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ha_id")
    args = parser.parse_args()

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
        homeconnect_etl = HomeConnectETL(engine, args.ha_id)
        homeconnect_etl.run()

        # Add a small sleep to prevent a direct loop without pauses when something
        # goes wrong
        sleep(0.1)
