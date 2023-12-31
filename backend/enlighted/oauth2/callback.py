from fastapi import FastAPI
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from enlighted.oauth2.models import AccessToken, Base, RefreshToken
from enlighted.oauth2.oauth2 import AuthorizationCodeGrant


def create_app(
    engine: Engine,
    session: Session,
    authorization_code_grant: AuthorizationCodeGrant,
) -> FastAPI:
    app: FastAPI = FastAPI()

    """Create all tables."""
    Base.metadata.create_all(engine)

    @app.get("/callback")
    async def callback(code: str, state: str) -> str:
        """Store the refresh token.Callback endpoint."""

        # TODO Check state

        resp = authorization_code_grant.exchange_code_for_access_token(code)

        # Get access token and refresh token and store tokens
        # Have the access token 'expire' early to force obtaining a new refresh token
        AccessToken.store_token(session, resp["access_token"], resp["expires_in"], 0.9)
        RefreshToken.store_token(session, resp["refresh_token"], resp["expires_in"])

        return "Access and refresh tokens succesfully stored."

    return app
