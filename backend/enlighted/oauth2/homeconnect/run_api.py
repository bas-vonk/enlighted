import uvicorn

from enlighted.db import AuthDbConfig, get_engine, get_session
from enlighted.oauth2.callback import create_app
from enlighted.oauth2.homeconnect.oauth2 import \
    HomeConnectAuthorizationCodeGrant
from enlighted.oauth2.models import AccessToken, RefreshToken

engine = get_engine(AuthDbConfig())
session = get_session({AccessToken: AuthDbConfig(), RefreshToken: AuthDbConfig()})

app = create_app(engine, session, HomeConnectAuthorizationCodeGrant(session))


if __name__ == "__main__":
    # Fire up the API
    uvicorn.run(
        "enlighted.oauth2.homeconnect.run_api:app",
        host="0.0.0.0",
        port=80,
        reload=True,
    )
