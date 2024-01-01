import uuid

import redis
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from enlighted.db import GoldDbConfig, SilverDbConfig, get_session
from enlighted.pipelines.bronze2silver.models import (
    Event,
    ValueTimestamp,
    ValueTimestampHighFrequency,
    ValueTimeWindow,
)
from enlighted.pipelines.silver2gold.models import Insight

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

session = get_session(
    {
        Insight: GoldDbConfig(),
        Event: SilverDbConfig(),
        ValueTimestamp: SilverDbConfig(),
        ValueTimestampHighFrequency: SilverDbConfig(),
        ValueTimeWindow: SilverDbConfig(),
    }
)

STREAM_DELAY = 1  # second
RETRY_TIMEOUT = 15000  # milisecond


@app.get("/bronze/live_power")
def live_power():
    def event_generator():
        redis_obj = redis.Redis(host="192.168.2.202", port=6379, decode_responses=True)

        channel = redis_obj.pubsub()
        channel.subscribe("tibber.LiveMeasurement")

        for message in channel.listen():
            try:
                yield {
                    "event": "message",
                    "id": str(uuid.uuid4()),
                    "retry": RETRY_TIMEOUT,
                    "data": message["data"],
                }
            except TypeError:
                pass

    return EventSourceResponse(event_generator())


@app.get("/silver/value_timestamp")
def value_timestamp(
    device_name: str,
    observation_name: str,
    observed_at_lower_bound: int = 0,
    limit: int = None,
):
    data = ValueTimestamp.read(
        session=session,
        device_name=device_name,
        observation_name=observation_name,
        observed_at_lower_bound=observed_at_lower_bound,
        limit=limit,
    )
    return {
        "observation_name": observation_name,
        "device_name": device_name,
        "data": data,
    }


@app.get("/gold/insight")
def insight(insight_name: str):
    insight = Insight.read(
        session=session,
        insight_name=insight_name,
    )
    return {
        "insight_name": insight_name,
        "insight": insight["insight"],
        "observed_at": insight["observed_at"],
    }


if __name__ == "__main__":
    # Fire up the API
    uvicorn.run(
        "enlighted.apis.run_api:app",
        host="0.0.0.0",
        port=80,
        reload=True,
    )
