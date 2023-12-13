import datetime
import logging
from time import sleep

from enlighted.db import AuthDbConfig, get_engine, get_session
from enlighted.oauth2.homeconnect.oauth2 import (
    HomeConnectAuthorizationCodeGrant,
    HomeConnectRefreshTokenGrant,
)
from enlighted.oauth2.models import AccessToken, Base, RefreshToken
from enlighted.oauth2.oauth2 import get_valid_token
from scheduler import Scheduler  # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HomeConnect Auth Agent")

if __name__ == "__main__":
    engine = get_engine(AuthDbConfig())
    session = get_session({AccessToken: AuthDbConfig(), RefreshToken: AuthDbConfig()})

    # Ensure all tables exist.
    Base.metadata.create_all(engine)

    schedule = Scheduler()
    schedule.minutely(
        datetime.time(second=0),
        lambda: get_valid_token(  # type: ignore
            session,
            HomeConnectRefreshTokenGrant(session),
            HomeConnectAuthorizationCodeGrant(session),
        ),
    )

    while True:
        schedule.exec_jobs()
        sleep(1)
