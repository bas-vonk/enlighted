import base64
from typing import Dict

from sqlalchemy.engine import Engine

from minimal_footprint.integrations.enphase.config import EnphaseSettings
from minimal_footprint.oauth2.oauth2 import AuthorizationCodeGrant, RefreshTokenGrant
from minimal_footprint.utils import add_query_params_to_url


class EnphaseOAuth2:
    def __init__(self) -> None:
        self.settings = EnphaseSettings()

    @property
    def basic_auth_token(self) -> str:
        """The basic auth token."""
        string_to_encode = f"{self.settings.client_id}:{self.settings.client_secret}"
        return base64.b64encode(string_to_encode.encode()).decode()

    @property
    def headers(self) -> Dict[str, str]:
        """The HTTP headers to be used for calls to the Auth endpoint."""
        return {"Authorization": f"Basic {self.basic_auth_token}"}


class EnphaseAuthorizationCodeGrant(EnphaseOAuth2, AuthorizationCodeGrant):
    def __init__(self, engine: Engine) -> None:
        EnphaseOAuth2.__init__(self)
        AuthorizationCodeGrant.__init__(self, engine, self.settings.api_token_url)

    @property
    def authorization_url(self) -> str:
        return add_query_params_to_url(
            self.settings.api_authorization_code_url,
            {
                "response_type": "code",
                "client_id": self.settings.client_id,
                "redirect_uri": self.settings.redirect_uri,
                "state": self.settings.state,
            },
        )

    def get_request_body(self, code: str) -> Dict[str, str]:
        return {
            "grant_type": self.grant_type,
            "redirect_uri": self.settings.redirect_uri,
            "code": code,
        }


class EnphaseRefreshTokenGrant(EnphaseOAuth2, RefreshTokenGrant):
    def __init__(self, engine: Engine) -> None:
        EnphaseOAuth2.__init__(self)
        RefreshTokenGrant.__init__(self, engine, self.settings.api_token_url)

    def get_request_body(self, refresh_token: str) -> Dict[str, str]:
        return {
            "grant_type": self.grant_type,
            "redirect_uri": self.settings.redirect_uri,
            "refresh_token": refresh_token,
        }