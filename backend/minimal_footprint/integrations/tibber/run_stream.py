import asyncio
import json
import logging

import aiohttp
import redis
import tibber
from minimal_footprint.db import get_engine
from minimal_footprint.integrations.tibber.config import TibberSettings
from minimal_footprint.integrations.tibber.models import Base, LiveTicker
from minimal_footprint.utils import ts_str_to_unix
from redis import Redis
from sqlalchemy.engine import Engine

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("Tibber Stream")

settings = TibberSettings()


class TibberStream:
    def __init__(self, engine: Engine, redis_obj: Redis):
        self.engine = engine
        self.redis_obj = redis_obj

    def _callback(self, message):
        # Get the data from the message. If there is no 'data' in the message, do nothing
        data = message.get("data")
        if data is None:
            return

        row = data.get("liveMeasurement")
        self.redis_obj.publish("tibber", json.dumps(row))
        LiveTicker.upsert(
            self.engine,
            {
                "timestamp": ts_str_to_unix(row["timestamp"], settings.api_ts_str_fmt),
                "power_watt": row["power"],
                "power_production_watt": row["powerProduction"],
                "current_l1": row["currentL1"],
                "current_l2": row["currentL2"],
                "current_l3": row["currentL3"],
            },
        )

    async def run(self):
        async with aiohttp.ClientSession() as session:
            tibber_connection = tibber.Tibber(
                settings.api_token, websession=session, user_agent="minimal_footprint"
            )
            await tibber_connection.update_info()

        # Get the home (there is only one) and subscribe to this home
        home = tibber_connection.get_homes()[0]
        await home.rt_subscribe(self._callback)

        # Ensure the job never ends
        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    # Get an engine
    engine = get_engine(
        settings.db_username,
        settings.db_password,
        settings.db_hostname,
        settings.db_database,
        settings.db_port,
    )

    """Create all tables."""
    Base.metadata.create_all(engine)

    # Create Redis object
    redis_obj = redis.Redis(host="172.19.0.4", port=6379, decode_responses=True)

    # Loop until the job ends
    loop = asyncio.get_event_loop()
    loop.run_until_complete(TibberStream(engine, redis_obj).run())
