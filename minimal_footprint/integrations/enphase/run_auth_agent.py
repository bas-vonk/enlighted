import logging
from time import sleep

from minimal_footprint.db import get_engine
from minimal_footprint.integrations.enphase.config import EnphaseSettings
from minimal_footprint.integrations.enphase.oauth2 import (
    EnphaseAuthorizationCodeGrant,
    EnphaseRefreshTokenGrant,
)
from minimal_footprint.oauth2.oauth2 import get_valid_token
from minimal_footprint.utils import now_hrf

settings = EnphaseSettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Enphase Auth Agent")

if __name__ == "__main__":
    engine = get_engine(
        settings.db_username,
        settings.db_password,
        settings.db_hostname,
        settings.db_database,
        settings.db_port,
    )

    while True:
        refresh_token_grant = EnphaseRefreshTokenGrant(engine)
        authorization_code_grant = EnphaseAuthorizationCodeGrant(engine)

        access_token = get_valid_token(engine, refresh_token_grant)

        if not access_token:
            msg = f"Re-authorize at: {authorization_code_grant.authorization_url}"
            logger.warning(msg)

        logger.info(f"Still running at {now_hrf()}")
        sleep(300)
