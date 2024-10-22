import datetime
import logging
from time import sleep

from enlighted.db import AuthDbConfig, get_engine, get_session
from enlighted.oauth2.models import AccessToken, Base
from enlighted.oauth2.nibe.config import NibeSettings
from enlighted.oauth2.nibe.oauth2 import NibeClientCredentialsGrant
from scheduler import Scheduler  # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Nibe Auth Agent")

settings = NibeSettings()

if __name__ == "__main__":
    engine = get_engine(AuthDbConfig())
    session = get_session({AccessToken: AuthDbConfig()})

    # Ensure all tables exist.
    Base.metadata.create_all(engine)

    # Run the job
    schedule = Scheduler()
    schedule.minutely(
        datetime.time(second=0),
        lambda: NibeClientCredentialsGrant(
            session, settings.api_token_url
        ).get_valid_token(),
    )

    while True:
        schedule.exec_jobs()
        sleep(1)
