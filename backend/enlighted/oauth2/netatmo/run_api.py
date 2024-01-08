import uvicorn
from enlighted.db import AuthDbConfig, get_engine, get_session
from enlighted.oauth2.callback import create_app
from enlighted.oauth2.models import AccessToken, RefreshToken
from enlighted.oauth2.netatmo.oauth2 import NetatmoAuthorizationCodeGrant

engine = get_engine(AuthDbConfig())
session = get_session({AccessToken: AuthDbConfig(), RefreshToken: AuthDbConfig()})

app = create_app(engine, session, NetatmoAuthorizationCodeGrant(session))


if __name__ == "__main__":
    # Fire up the API
    uvicorn.run(
        "enlighted.oauth2.netatmo.run_api:app",
        host="0.0.0.0",
        port=80,
        reload=True,
    )
