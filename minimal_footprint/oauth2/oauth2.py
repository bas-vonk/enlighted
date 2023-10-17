import logging
from typing import Optional

import requests
from sqlalchemy.engine import Engine

from minimal_footprint.oauth2.models import AccessToken, RefreshToken
from minimal_footprint.utils import now

logger = logging.getLogger()


class OAuth2:
    def __init__(self, engine: Engine):
        self.engine = engine

    @property
    def headers(self) -> dict:
        raise NotImplementedError

    def call_token_endpoint(self, request_body: dict) -> dict:
        return requests.post(
            self.settings.api_token_url,
            data=request_body,
            headers=self.headers,
        ).json()


class AuthorizationCodeGrant(OAuth2):
    def __init__(self, engine):
        OAuth2.__init__(self, engine)
        self.grant_type = "authorization_code"

    @property
    def authorization_url(self):
        raise NotImplementedError

    def get_request_body(self):
        raise NotImplementedError

    def exchange_code_for_access_token(self, code):
        return self.call_token_endpoint(self.get_request_body(code))


class RefreshTokenGrant(OAuth2):
    def __init__(self, engine):
        OAuth2.__init__(self, engine)
        self.grant_type = "refresh_token"

    def get_request_body(self):
        raise NotImplementedError

    def exchange_refresh_token_for_access_token(self, refresh_token):
        return self.call_token_endpoint(self.get_request_body(refresh_token))


def get_valid_token(
    engine: Engine, refresh_token_grant: RefreshTokenGrant
) -> Optional[str]:
    # Get the most recent access token and check that it's not expired
    # If it's valid, use it directly
    access_token = AccessToken.get_most_recent(engine)
    if access_token is not None and access_token["expires_at"] > now() + 5:
        return access_token["access_token"]

    # If no refresh token is found or it's expired (or about to expire), return None
    refresh_token = RefreshToken.get_most_recent(engine)
    if refresh_token is None or refresh_token["expires_at"] < now() + 5:
        return None

    # Get a new access token from the valid refresh token and store the
    # access token and newly obtained refresh token.
    refresh_token = refresh_token["refresh_token"]
    res = refresh_token_grant.exchange_refresh_token_for_access_token(refresh_token)

    # Store the results
    AccessToken.store_token(engine, res["access_token"], res["expires_in"], 0.9)
    RefreshToken.store_token(engine, res["refresh_token"], res["expires_in"])
    logger.info("New access/refresh tokens stored.")

    # Return the access token
    return res["access_token"]
