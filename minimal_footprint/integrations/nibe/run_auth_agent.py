import datetime
import logging
from time import sleep

from scheduler import Scheduler  # type: ignore

from minimal_footprint.db import get_engine
from minimal_footprint.integrations.nibe.config import NibeSettings
from minimal_footprint.integrations.nibe.oauth2 import (
    NibeAuthorizationCodeGrant,
    NibeRefreshTokenGrant,
)
from minimal_footprint.oauth2.oauth2 import get_valid_token

settings = NibeSettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Nibe Auth Agent")

if __name__ == "__main__":
    engine = get_engine(
        settings.db_username,
        settings.db_password,
        settings.db_hostname,
        settings.db_database,
        settings.db_port,
    )

    schedule = Scheduler()
    schedule.minutely(
        datetime.time(second=0),
        lambda: get_valid_token(   # type: ignore
            engine,
            NibeRefreshTokenGrant(engine),
            NibeAuthorizationCodeGrant(engine),
        ),
    )

    while True:
        schedule.exec_jobs()
        sleep(1)
