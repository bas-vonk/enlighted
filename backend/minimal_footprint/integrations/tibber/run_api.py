import json
import uuid

import redis
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STREAM_DELAY = 1  # second
RETRY_TIMEOUT = 15000  # milisecond


@app.get("/live_power")
def live_power(request: Request):
    def event_generator():
        redis_obj = redis.Redis(host="192.168.2.202", port=6379, decode_responses=True)

        channel = redis_obj.pubsub()
        channel.subscribe("tibber")

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


if __name__ == "__main__":
    # Fire up the API
    uvicorn.run(
        "minimal_footprint.integrations.tibber.run_api:app",
        host="0.0.0.0",
        port=80,
        reload=True,
    )
