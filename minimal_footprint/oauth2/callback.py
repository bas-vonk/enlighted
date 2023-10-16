from fastapi import FastAPI

from minimal_footprint.db import create_all_tables
from minimal_footprint.oauth2.models import AccessToken, Base, RefreshToken


def create_app(settings, engine, authorization_code_grant):
    app = FastAPI()

    # Create the database tables and an engine
    create_all_tables(Base, engine)

    @app.get("/callback")
    async def callback(code: str, state: str):
        """Store the refresh token.Callback endpoint."""

        # Check the state
        assert state == settings.state  # TODO Make state dynamic, this is pointless

        resp = authorization_code_grant.exchange_code_for_access_token(code)

        # Get access token and refresh token and store tokens
        # Have the access token 'expire' early to force obtaining a new refresh token
        AccessToken.store_token(engine, resp["access_token"], resp["expires_in"], 0.9)
        RefreshToken.store_token(engine, resp["refresh_token"], resp["expires_in"])

        return "Access and refresh tokens succesfully stored."

    return app
