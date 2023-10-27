import uvicorn

from minimal_footprint.db import get_engine
from minimal_footprint.integrations.homeconnect.config import HomeConnectSettings
from minimal_footprint.integrations.homeconnect.oauth2 import (
    HomeConnectAuthorizationCodeGrant,
)
from minimal_footprint.oauth2.callback import create_app

settings = HomeConnectSettings()
engine = get_engine(
    settings.db_username,
    settings.db_password,
    settings.db_hostname,
    settings.db_database,
    settings.db_port,
)

app = create_app(engine, HomeConnectAuthorizationCodeGrant(engine))


if __name__ == "__main__":
    # Fire up the API
    uvicorn.run(
        "minimal_footprint.integrations.homeconnect.run_api:app",
        host="0.0.0.0",
        port=80,
        reload=True,
    )
