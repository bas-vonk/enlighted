import logging
from typing import Dict, Optional

import requests
from sqlalchemy.engine import Engine
from typing_extensions import TypedDict

from minimal_footprint.oauth2.models import (
    AccessToken,
    AccessTokenRow,
    RefreshToken,
    RefreshTokenRow,
)
from minimal_footprint.utils import now, now_hrf

logger = logging.getLogger()

TokenResponse = TypedDict(
    "TokenResponse", {"access_token": str, "refresh_token": str, "expires_in": int}
)


class OAuth2:
    def __init__(self, engine: Engine, api_token_url: str):
        self.engine = engine
        self.api_token_url = api_token_url

    @property
    def headers(self) -> Dict[str, str]:
        raise NotImplementedError

    def call_token_endpoint(self, request_body: Dict[str, str]) -> TokenResponse:
        return requests.post(
            self.api_token_url,
            data=request_body,
            headers=self.headers,
        ).json()


class AuthorizationCodeGrant(OAuth2):
    def __init__(self, engine: Engine, api_token_url: str) -> None:
        OAuth2.__init__(self, engine, api_token_url)
        self.grant_type = "authorization_code"

    @property
    def authorization_url(self) -> str:
        raise NotImplementedError

    def get_request_body(self, code: str) -> Dict[str, str]:
        raise NotImplementedError

    def exchange_code_for_access_token(self, code: str) -> TokenResponse:
        return self.call_token_endpoint(self.get_request_body(code))


class RefreshTokenGrant(OAuth2):
    def __init__(self, engine: Engine, api_token_url: str) -> None:
        OAuth2.__init__(self, engine, api_token_url)
        self.grant_type = "refresh_token"

    def get_request_body(self, refresh_token: str) -> Dict[str, str]:
        raise NotImplementedError

    def exchange_refresh_token_for_access_token(
        self, refresh_token: str
    ) -> TokenResponse:
        return self.call_token_endpoint(self.get_request_body(refresh_token))


def get_valid_token(
    engine: Engine,
    refresh_token_grant: RefreshTokenGrant,
    authorization_code_grant: AuthorizationCodeGrant,
) -> Optional[str]:
    # Get the most recent access token and check that it's not expired
    # If it's valid, use it directly
    access_token_row: AccessTokenRow | None = AccessToken.get_most_recent(engine)
    if access_token_row is not None and access_token_row["expires_at"] > now() + 5:
        return access_token_row["access_token"]

    # If no refresh token is found or it's expired (or about to expire), return None
    refresh_token_row: RefreshTokenRow | None = RefreshToken.get_most_recent(engine)
    if refresh_token_row is None or refresh_token_row["expires_at"] < now() + 5:
        logger.warning("No valid auth/refresh tokens found. Re-authorize.")
        logger.info(f"Auth URL: {authorization_code_grant.authorization_url}")
        return None

    # Get a new access token from the valid refresh token and store the
    # access token and newly obtained refresh token.
    refresh_token: str = refresh_token_row["refresh_token"]
    response = refresh_token_grant.exchange_refresh_token_for_access_token(
        refresh_token
    )

    # Store the results
    AccessToken.store_token(
        engine, response["access_token"], response["expires_in"], 0.75
    )
    RefreshToken.store_token(engine, response["refresh_token"], response["expires_in"])
    logger.info(f"New access/refresh tokens stored at {now_hrf()}.")

    # Return the access token
    return response["access_token"]
