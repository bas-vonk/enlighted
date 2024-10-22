from typing import Dict

from enlighted.oauth2.nibe.config import NibeSettings
from enlighted.oauth2.oauth2 import ClientCredentialsGrant
from sqlalchemy.orm import Session


class NibeOAuth2:
    def __init__(self) -> None:
        self.settings = NibeSettings()

    @property
    def headers(self) -> Dict[str, str]:
        """The HTTP headers to be used for calls to the Auth endpoint."""
        return {"Content-type": "application/x-www-form-urlencoded"}


class NibeClientCredentialsGrant(NibeOAuth2, ClientCredentialsGrant):
    def __init__(self, session: Session, api_token_url: str) -> None:
        NibeOAuth2.__init__(self)
        ClientCredentialsGrant.__init__(self, session, api_token_url)

    def get_request_body(self) -> Dict[str, str]:
        return {
            "grant_type": self.grant_type,
            "client_id": self.settings.client_id,
            "client_secret": self.settings.client_secret,
            "scope": self.settings.scope,
        }
