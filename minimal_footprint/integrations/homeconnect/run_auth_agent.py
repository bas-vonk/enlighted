import logging
from time import sleep

from minimal_footprint.db import get_engine
from minimal_footprint.integrations.homeconnect.config import HomeConnectSettings
from minimal_footprint.integrations.homeconnect.oauth2 import (
    HomeConnectAuthorizationCodeGrant,
    HomeConnectRefreshTokenGrant,
)
from minimal_footprint.oauth2.oauth2 import get_valid_token
from minimal_footprint.utils import now_hrf

settings = HomeConnectSettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HomeConnect Auth Agent")

if __name__ == "__main__":
    engine = get_engine(settings)

    while True:
        refresh_token_grant = HomeConnectRefreshTokenGrant(engine)
        authorization_code_grant = HomeConnectAuthorizationCodeGrant(engine)

        access_token = get_valid_token(engine, refresh_token_grant)

        if not access_token:
            msg = f"Re-authorize at: {authorization_code_grant.authorization_url}"
            logger.warning(msg)

        logger.info(f"Still running at {now_hrf()}")
        sleep(300)
