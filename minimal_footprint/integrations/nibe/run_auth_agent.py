import logging
from time import sleep

from minimal_footprint.db import get_engine
from minimal_footprint.integrations.nibe.config import NibeSettings
from minimal_footprint.integrations.nibe.oauth2 import (
    NibeAuthorizationCodeGrant,
    NibeRefreshTokenGrant,
)
from minimal_footprint.oauth2.oauth2 import OAuth2
from minimal_footprint.utils import now_hrf

settings = NibeSettings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Nibe Auth Agent")

if __name__ == "__main__":
    engine = get_engine(settings)

    while True:
        refresh_token_grant = NibeRefreshTokenGrant(engine)
        authorization_code_grant = NibeAuthorizationCodeGrant(engine)

        access_token = OAuth2.get_valid_token(engine, refresh_token_grant)

        if not access_token:
            msg = f"Re-authorize at: {authorization_code_grant.authorization_url}"
            logger.warning(msg)

        logger.info(f"Still running at {now_hrf()}")
        sleep(300)
