from typing import Dict

from sqlalchemy.orm import Session

from enlighted.oauth2.netatmo.config import NetatmoSettings
from enlighted.oauth2.oauth2 import AuthorizationCodeGrant, RefreshTokenGrant
from enlighted.utils import add_query_params_to_url


class NetatmoOAuth2:
    def __init__(self) -> None:
        self.settings = NetatmoSettings()

    @property
    def headers(self) -> Dict[str, str]:
        """The HTTP headers to be used for calls to the Auth endpoint."""
        return {"Content-type": "application/x-www-form-urlencoded"}


class NetatmoAuthorizationCodeGrant(NetatmoOAuth2, AuthorizationCodeGrant):
    def __init__(self, session: Session) -> None:
        NetatmoOAuth2.__init__(self)
        AuthorizationCodeGrant.__init__(self, session, self.settings.api_token_url)

    @property
    def authorization_url(self) -> str:
        return add_query_params_to_url(
            self.settings.api_authorization_code_url,
            {
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


class NetatmoRefreshTokenGrant(NetatmoOAuth2, RefreshTokenGrant):
    def __init__(self, session: Session) -> None:
        NetatmoOAuth2.__init__(self)
        RefreshTokenGrant.__init__(self, session, self.settings.api_token_url)

    def get_request_body(self, refresh_token: str) -> Dict[str, str]:
        return {
            "grant_type": self.grant_type,
            "refresh_token": refresh_token,
            "client_id": self.settings.client_id,
            "client_secret": self.settings.client_secret,
        }
