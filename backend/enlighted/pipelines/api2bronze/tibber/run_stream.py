import asyncio
import json
import logging

import aiohttp
import redis
import tibber
from enlighted.db import BronzeDbConfig, get_engine, get_session
from enlighted.pipelines.api2bronze.tibber.config import TibberSettings
from enlighted.pipelines.api2bronze.tibber.models import Base, LiveTicker
from enlighted.utils import ts_str_to_unix
from redis import Redis
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("Tibber Stream")

settings = TibberSettings()


class TibberStream:
    def __init__(self, session: Session, redis_obj: Redis):
        self.session = session
        self.redis_obj = redis_obj

    def _callback(self, message):
        # Get the data from the message. If there is no 'data' in the message, do nothing
        data = message.get("data")
        if data is None:
            return

        row = data.get("liveMeasurement")
        if row is None:
            return

        self.redis_obj.publish("tibber", json.dumps(row))
        live_ticker = LiveTicker.upsert(
            self.session,
            {
                **row,
                **{
                    "timestamp": ts_str_to_unix(
                        row["timestamp"], settings.api_ts_str_fmt
                    )
                },
            },
        )
        self.redis_obj.lpush("tibber.LiveTicker", live_ticker.id)
        logger.info(f"Power watt: {row['power']}")

    async def run(self):
        async with aiohttp.ClientSession() as session:
            tibber_connection = tibber.Tibber(
                settings.api_token, websession=session, user_agent="enlighted"
            )
            await tibber_connection.update_info()

        # Get the home (there is only one) and subscribe to this home
        home = tibber_connection.get_homes()[0]
        await home.rt_subscribe(self._callback)

        # Ensure the job never ends
        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    engine = get_engine(BronzeDbConfig())
    session = get_session({LiveTicker: BronzeDbConfig()})

    """Create all tables."""
    Base.metadata.create_all(engine)

    # Create Redis object
    redis_obj = redis.Redis(host="172.19.0.4", port=6379, decode_responses=True)

    # Loop until the job ends
    loop = asyncio.get_event_loop()
    loop.run_until_complete(TibberStream(session, redis_obj).run())
