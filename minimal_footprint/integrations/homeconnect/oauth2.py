from minimal_footprint.integrations.homeconnect.config import HomeConnectSettings
from minimal_footprint.oauth2.oauth2 import AuthorizationCodeGrant, RefreshTokenGrant
from minimal_footprint.utils import add_query_params_to_url


class HomeConnectOAuth2:
    def __init__(self):
        self.settings = HomeConnectSettings()

    @property
    def headers(self):
        """The HTTP headers to be used for calls to the Auth endpoint."""
        return {"Content-type": "application/x-www-form-urlencoded"}


class HomeConnectAuthorizationCodeGrant(HomeConnectOAuth2, AuthorizationCodeGrant):
    def __init__(self, engine):
        HomeConnectOAuth2.__init__(self)
        AuthorizationCodeGrant.__init__(self, engine)

    @property
    def authorization_url(self):
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

    def get_request_body(self, code):
        return {
            "grant_type": self.grant_type,
            "client_id": self.settings.client_id,
            "client_secret": self.settings.client_secret,
            "code": code,
            "redirect_uri": self.settings.redirect_uri,
        }


class HomeConnectRefreshTokenGrant(HomeConnectOAuth2, RefreshTokenGrant):
    def __init__(self, engine):
        HomeConnectOAuth2.__init__(self)
        RefreshTokenGrant.__init__(self, engine)

    def get_request_body(self, refresh_token):
        return {
            "grant_type": self.grant_type,
            "refresh_token": refresh_token,
            "client_id": self.settings.client_id,
            "client_secret": self.settings.client_secret,
        }
