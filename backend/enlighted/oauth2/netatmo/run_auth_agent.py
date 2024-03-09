import datetime
import logging
from time import sleep

from scheduler import Scheduler  # type: ignore

from enlighted.db import AuthDbConfig, get_engine, get_session
from enlighted.oauth2.models import AccessToken, Base, RefreshToken
from enlighted.oauth2.netatmo.oauth2 import (
    NetatmoAuthorizationCodeGrant,
    NetatmoRefreshTokenGrant,
)
from enlighted.oauth2.oauth2 import get_valid_token

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Netatmo Auth Agent")

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
            NetatmoRefreshTokenGrant(session),
            NetatmoAuthorizationCodeGrant(session),
        ),
    )

    while True:
        schedule.exec_jobs()
        sleep(1)
