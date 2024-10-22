import logging
from typing import Dict, Optional

import requests
from sqlalchemy.orm import Session
from typing_extensions import TypedDict

from enlighted.oauth2.models import AccessToken, AccessTokenRow
from enlighted.utils import now, now_hrf

logger = logging.getLogger()

TokenResponse = TypedDict("TokenResponse", {"access_token": str, "expires_in": int})


class OAuth2:
    def __init__(self, session: Session, api_token_url: str):
        self.session = session
        self.api_token_url = api_token_url

    @property
    def headers(self) -> Dict[str, str]:
        raise NotImplementedError

    def call_token_endpoint(self, request_body: Dict[str, str]) -> TokenResponse:
        return requests.post(
            self.api_token_url, data=request_body, headers=self.headers, timeout=10
        ).json()


class ClientCredentialsGrant(OAuth2):
    def __init__(self, session: Session, api_token_url: str) -> None:
        OAuth2.__init__(self, session, api_token_url)
        self.grant_type = "client_credentials"

    def get_request_body(self) -> Dict[str, str]:
        raise NotImplementedError

    def get_valid_token(self) -> Optional[str]:
        # Get the most recent access token and check that it's not expired
        # If it's valid, use it directly
        access_token_row: AccessTokenRow | None = AccessToken.get_most_recent(
            self.session
        )
        if access_token_row is not None and access_token_row["expires_at"] > now() + 5:
            logger.info(f"Access token still valid at {now_hrf()}.")
            return access_token_row["access_token"]

        response: TokenResponse = self.exchange_client_credentials_for_access_token()
        AccessToken.store_token(
            self.session, response["access_token"], response["expires_in"], 0.50
        )
        logger.info(f"New access token stored at {now_hrf()}.")

        # Return the access token
        return response["access_token"]

    def exchange_client_credentials_for_access_token(self) -> TokenResponse:
        return self.call_token_endpoint(self.get_request_body())


class AuthorizationCodeGrant(OAuth2):
    def __init__(self, session: Session, api_token_url: str) -> None:
        OAuth2.__init__(self, session, api_token_url)
        self.grant_type = "authorization_code"

    @property
    def authorization_url(self) -> str:
        raise NotImplementedError

    def get_request_body(self, code: str) -> Dict[str, str]:
        raise NotImplementedError

    def exchange_code_for_access_token(self, code: str) -> TokenResponse:
        return self.call_token_endpoint(self.get_request_body(code))


class RefreshTokenGrant(OAuth2):
    def __init__(self, session: Session, api_token_url: str) -> None:
        OAuth2.__init__(self, session, api_token_url)
        self.grant_type = "refresh_token"

    def get_request_body(self, refresh_token: str) -> Dict[str, str]:
        raise NotImplementedError

    def exchange_refresh_token_for_access_token(
        self, refresh_token: str
    ) -> TokenResponse:
        return self.call_token_endpoint(self.get_request_body(refresh_token))
