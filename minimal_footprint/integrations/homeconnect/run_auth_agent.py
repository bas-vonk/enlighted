import datetime
import logging
from time import sleep

from scheduler import Scheduler  # type: ignore

from minimal_footprint.db import get_engine
from minimal_footprint.integrations.homeconnect.config import HomeConnectSettings
from minimal_footprint.integrations.homeconnect.oauth2 import (
    HomeConnectAuthorizationCodeGrant,
    HomeConnectRefreshTokenGrant,
)
from minimal_footprint.oauth2.oauth2 import get_valid_token

settings = HomeConnectSettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HomeConnect Auth Agent")

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
            HomeConnectRefreshTokenGrant(engine),
            HomeConnectAuthorizationCodeGrant(engine),
        ),
    )

    while True:
        schedule.exec_jobs()
        sleep(1)
