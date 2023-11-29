import uvicorn

from minimal_footprint.db import get_engine
from minimal_footprint.integrations.enphase.config import EnphaseSettings
from minimal_footprint.integrations.enphase.oauth2 import EnphaseAuthorizationCodeGrant
from minimal_footprint.oauth2.callback import create_app

settings = EnphaseSettings()
engine = get_engine(
    settings.db_username,
    settings.db_password,
    settings.db_hostname,
    settings.db_database,
    settings.db_port,
)

app = create_app(engine, EnphaseAuthorizationCodeGrant(engine))


if __name__ == "__main__":
    # Fire up the API
    uvicorn.run(
        "minimal_footprint.integrations.enphase.run_api:app",
        host="0.0.0.0",
        port=80,
        reload=True,
    )
