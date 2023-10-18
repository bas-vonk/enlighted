from typing import Dict

from sqlalchemy.engine import Engine

from minimal_footprint.integrations.nibe.config import NibeSettings
from minimal_footprint.oauth2.oauth2 import AuthorizationCodeGrant, RefreshTokenGrant
from minimal_footprint.utils import add_query_params_to_url


class NibeOAuth2:
    def __init__(self) -> None:
        self.settings = NibeSettings()

    @property
    def headers(self) -> Dict[str, str]:
        """The HTTP headers to be used for calls to the Auth endpoint."""
        return {"Content-type": "application/x-www-form-urlencoded"}


class NibeAuthorizationCodeGrant(NibeOAuth2, AuthorizationCodeGrant):
    def __init__(self, engine: Engine) -> None:
        NibeOAuth2.__init__(self)
        AuthorizationCodeGrant.__init__(self, engine, self.settings.api_token_url)

    @property
    def authorization_url(self) -> str:
        return add_query_params_to_url(
            self.settings.api_authorization_code_url,
            {
                "response_type": "code",
                "client_id": self.settings.client_id,
                "scope": self.settings.scope,
                "redirect_uri": self.settings.redirect_uri,
                "state": self.settings.state,
            },
        )

    def get_request_body(self, code: str) -> Dict[str, str]:
        return {
            "grant_type": self.grant_type,
            "client_id": self.settings.client_id,
            "client_secret": self.settings.client_secret,
            "code": code,
            "redirect_uri": self.settings.redirect_uri,
            "scope": self.settings.scope,
        }


class NibeRefreshTokenGrant(NibeOAuth2, RefreshTokenGrant):
    def __init__(self, engine: Engine):
        NibeOAuth2.__init__(self)
        RefreshTokenGrant.__init__(self, engine, self.settings.api_token_url)

    def get_request_body(self, refresh_token: str) -> Dict[str, str]:
        return {
            "grant_type": self.grant_type,
            "refresh_token": refresh_token,
            "client_id": self.settings.client_id,
            "client_secret": self.settings.client_secret,
        }
