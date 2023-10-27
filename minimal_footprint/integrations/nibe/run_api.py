import uvicorn

from minimal_footprint.db import get_engine
from minimal_footprint.integrations.nibe.config import NibeSettings
from minimal_footprint.integrations.nibe.oauth2 import NibeAuthorizationCodeGrant
from minimal_footprint.oauth2.callback import create_app

settings = NibeSettings()
engine = get_engine(
    settings.db_username,
    settings.db_password,
    settings.db_hostname,
    settings.db_database,
    settings.db_port,
)

app = create_app(engine, NibeAuthorizationCodeGrant(engine))


if __name__ == "__main__":
    # Fire up the API
    uvicorn.run(
        "minimal_footprint.integrations.nibe.run_api:app",
        host="0.0.0.0",
        port=80,
        reload=True,
    )
