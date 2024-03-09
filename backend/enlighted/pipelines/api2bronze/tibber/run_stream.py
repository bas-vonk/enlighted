import asyncio
import json
import logging
import signal
import time
from asyncio.exceptions import CancelledError

import redis
from gql import Client, gql
from gql.transport.websockets import WebsocketsTransport
from websockets.exceptions import ConnectionClosedError

from enlighted.db import BronzeDbConfig, get_engine, get_session
from enlighted.pipelines.api2bronze.tibber.config import TibberSettings
from enlighted.pipelines.api2bronze.tibber.models import Base, LiveMeasurement
from enlighted.utils import ts_str_to_unix

# Set the right loglevels
logging.basicConfig(level=logging.INFO)
logging.getLogger("gql.transport.websockets").setLevel(logging.WARNING)

logger = logging.getLogger("Tibber Stream")

settings = TibberSettings()

RECONNECTION_TIMEOUT_START_VALUE = 0.5


class TibberStream:
    def __init__(self, session, redis_obj):
        self.session = session
        self.redis_obj = redis_obj

        self.client = None
        self.connection = None

    @property
    def query(self):
        """Define the GraphQL query for the subscription."""

        return """
        subscription {
            liveMeasurement(homeId: "bd831f24-ea3a-4118-9fc4-25b8da836baf") {
                accumulatedCost
                accumulatedReward
                accumulatedProduction
                accumulatedConsumption
                accumulatedProductionLastHour
                accumulatedConsumptionLastHour
                averagePower
                currency
                currentL1
                currentL2
                currentL3
                lastMeterConsumption
                lastMeterProduction
                maxPower
                maxPowerProduction
                minPower
                minPowerProduction
                power
                powerFactor
                powerProduction
                powerProductionReactive
                powerReactive
                signalStrength
                timestamp
                voltagePhase1
                voltagePhase2
                voltagePhase3
            }
        }
        """

    def _callback(self, message):
        """Process the message."""

        # If there's no 'liveMeasurement' key in the message, do nothing
        if "liveMeasurement" not in message:
            return

        live_measurement = message["liveMeasurement"]

        # Upsert into the Bronze layer
        row = LiveMeasurement.upsert(
            self.session,
            {
                **live_measurement,
                **{
                    "timestamp": ts_str_to_unix(
                        live_measurement["timestamp"], settings.api_ts_str_fmt
                    )
                },
            },
        )
        self.redis_obj.lpush("tibber.LiveMeasurement", row.id)

        # Push to the message stream
        self.redis_obj.publish("tibber.LiveMeasurement", json.dumps(live_measurement))

        logger.info(
            f"Timestamp of latest receive message is {live_measurement['timestamp']}."
        )

    @property
    def transport(self):
        return WebsocketsTransport(
            url=settings.wss_url,
            headers={
                "Authorization": f"Bearer {settings.api_token}",
                "User-Agent": "Enlighted/0.0.1",
            },
        )

    async def connect(self):
        """Connect."""
        self.client = Client(transport=self.transport, fetch_schema_from_transport=True)
        self.connection = await self.client.connect_async(reconnecting=False)

        logger.info("Connection established.")
        return

    async def disconnect(self):
        """Disconnect."""
        if self.client and self.connection:
            await self.client.close_async()
            logger.info("Socket connection closed.")
        else:
            logger.info("Socket connection didn't need to be closed.")

        return

    async def listen(self):
        """Listen for messages."""

        await self.connect()

        async for message in self.connection.subscribe(gql(self.query)):
            self._callback(message)

    async def signal_handler(self, loop, signame):
        """Handle signals."""

        logger.info(f"Signal handler invoked for signal {signame}.")
        await self.disconnect()

        loop.stop()
        return


async def main():
    # Database
    engine = get_engine(BronzeDbConfig())
    session = get_session({LiveMeasurement: BronzeDbConfig()})

    # Redis
    redis_obj = redis.Redis(host="192.168.2.201", port=6379, decode_responses=True)

    """Ensure all tables exist."""
    Base.metadata.create_all(engine)

    # Initializing the class needs to happen outside of the while True,
    # to properly deal with the reconnection timeouts
    tibber_stream = TibberStream(session=session, redis_obj=redis_obj)

    # Get asyncio event loop
    loop = asyncio.get_event_loop()

    # Add signal handler
    for s in {"SIGINT", "SIGTERM"}:
        loop.add_signal_handler(
            getattr(signal, s),
            lambda s=s: asyncio.create_task(tibber_stream.signal_handler(loop, s)),
        )

    try:
        await tibber_stream.listen()
    except ConnectionClosedError:
        logger.info("ConnectionClosedError caught.")
    except CancelledError:
        logger.info("CancelledError caught.")
    finally:
        await tibber_stream.disconnect()
        logger.info("Successfully shutdown the process.")


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except RuntimeError as e:
            logger.error("RuntimeError caught.")
            logger.info(e)

        time.sleep(60)
