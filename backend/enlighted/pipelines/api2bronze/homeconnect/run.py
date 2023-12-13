import argparse
import json
import logging
from collections.abc import Generator
from time import sleep
from typing import Dict, Union

import redis
import sseclient
from requests import Response
from requests.exceptions import ChunkedEncodingError
from sqlalchemy.orm import Session
from urllib3.exceptions import InvalidChunkLength, ProtocolError

from enlighted.db import AuthDbConfig, BronzeDbConfig, get_engine, get_session
from enlighted.oauth2.homeconnect.oauth2 import (
    HomeConnectAuthorizationCodeGrant, HomeConnectRefreshTokenGrant)
from enlighted.oauth2.models import AccessToken, RefreshToken
from enlighted.pipelines.api2bronze.base_etl import BaseETL
from enlighted.pipelines.api2bronze.homeconnect.config import \
    HomeConnectSettings
from enlighted.pipelines.api2bronze.homeconnect.models import (Base,
                                                               OperationState)
from enlighted.utils import now, now_hrf

settings = HomeConnectSettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HomeConnect ETL")


class HomeConnectETL(BaseETL):
    def __init__(self, session: Session, ha_id: int):
        self.session = session
        self.ha_id = ha_id

        BaseETL.__init__(
            self,
            session=self.session,
            etl_run_start_time=now(),
            is_stream=True,
            access_token=None,
            refresh_token_grant=HomeConnectRefreshTokenGrant(self.session),
            authorization_code_grant=HomeConnectAuthorizationCodeGrant(self.session),
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

                        yield {**item, **{"haId": message["haId"]}}
                        logger.info(f"OperationState message received at {now_hrf()}.")

                except json.decoder.JSONDecodeError:
                    logger.info(f"Empty message received at {now_hrf()}.")
        except (ChunkedEncodingError, InvalidChunkLength, ProtocolError, KeyError):
            logger.warning(f"Message stream interrupted at {now_hrf()}.")
            return  # According to PEP479: https://peps.python.org/pep-0479/

    def load(self, row: Dict[str, Union[str, int, float]]) -> None:
        operation_state = OperationState.upsert(self.session, row)
        redis_obj = redis.Redis(host="192.168.2.202", port=6379, decode_responses=True)
        redis_obj.lpush("homeconnect.OperationState", operation_state.id)

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

    engine = get_engine(BronzeDbConfig())
    session = get_session(
        {
            AccessToken: AuthDbConfig(),
            RefreshToken: AuthDbConfig(),
            OperationState: BronzeDbConfig(),
        }
    )

    """Create all tables."""
    Base.metadata.create_all(engine)

    while True:
        homeconnect_etl = HomeConnectETL(session, args.ha_id)
        homeconnect_etl.run()

        # Add a small sleep to prevent a direct loop without pauses when something
        # goes wrong
        sleep(0.1)
