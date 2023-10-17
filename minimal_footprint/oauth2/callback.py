from fastapi import FastAPI
from pydantic_settings import BaseSettings
from sqlalchemy.engine import Engine

from minimal_footprint.db import create_all_tables
from minimal_footprint.oauth2.models import AccessToken, Base, RefreshToken
from minimal_footprint.oauth2.oauth2 import AuthorizationCodeGrant


def create_app(
    settings: BaseSettings,
    engine: Engine,
    authorization_code_grant: AuthorizationCodeGrant,
) -> FastAPI:
    app: FastAPI = FastAPI()

    # Create the database tables and an engine
    create_all_tables(Base, engine)

    @app.get("/callback")
    async def callback(code: str, state: str) -> str:
        """Store the refresh token.Callback endpoint."""

        # Check the state
        assert state == settings.state  # TODO Make state dynamic, this is pointless

        resp: dict = authorization_code_grant.exchange_code_for_access_token(code)

        # Get access token and refresh token and store tokens
        # Have the access token 'expire' early to force obtaining a new refresh token
        AccessToken.store_token(engine, resp["access_token"], resp["expires_in"], 0.9)
        RefreshToken.store_token(engine, resp["refresh_token"], resp["expires_in"])

        return "Access and refresh tokens succesfully stored."

    return app
