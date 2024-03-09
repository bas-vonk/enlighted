import uuid
from typing import List

import pandas as pd
import redis
import uvicorn
from enlighted.db import GoldDbConfig, SilverDbConfig, get_session
from enlighted.pipelines.bronze2silver.models import (
    Event,
    ValueTimestamp,
    ValueTimeWindow,
)
from enlighted.pipelines.silver2gold.energy.utils import (
    replace_observed_at_with_window_start_end,
)
from enlighted.pipelines.silver2gold.models import Insight
from enlighted.utils import last_full_day
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

SECONDS_IN_HOUR = 3600
SECONDS_IN_MINUTE = 60

pd.set_option("display.max_rows", None)

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
        ValueTimeWindow: SilverDbConfig(),
    }
)

STREAM_DELAY = 1  # second
RETRY_TIMEOUT = 15000  # milisecond


@app.get("/bronze/live_power")
def live_power():
    def event_generator():
        redis_obj = redis.Redis(host="192.168.2.201", port=6379, decode_responses=True)

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


@app.get("/silver/nibe_measurements")
def nibe_measurements(observation_names: str):
    data = {}
    for observation_name in observation_names.split(","):
        data[observation_name] = ValueTimestamp.read(
            session=session,
            device_name="f1255pc",
            observation_name=observation_name,
            observed_at_lower_bound=0,
            limit=1,
        )[0]

    return data


@app.get("/gold/nibe_energy")
def nibe_energy():
    start_of_day = last_full_day()

    # Get the model for energy consumption
    model = Insight.read(
        session=session,
        insight_name="energy_consumption_model",
    )

    # Compute the energy consumption for individual components of the heat pump
    # and add it to a total
    total_energy_consumption = 0
    for observation_name in [
        "compressor_frequency",
        "heat_circuit_pump_speed",
        "brine_circuit_pump_speed",
    ]:
        df = pd.DataFrame.from_records(
            ValueTimestamp.read(
                session=session,
                device_name="f1255pc",
                observation_name=observation_name,
                observed_at_lower_bound=start_of_day,
                limit=None,
            )
        )

        # Create hourly windows
        replace_observed_at_with_window_start_end(df, SECONDS_IN_HOUR)

        # NOTE: This groupby assumes that the values (compressor frequency,
        #       heat_circuit_pump_speed, and brine_circuit_pump_speed) are
        #       registered every minute
        df = df.groupby(["window_start", "window_end"]).agg(
            value=("value", lambda values: sum(values) / SECONDS_IN_MINUTE)
        )
        df["value"] *= model["insight"]["coefficients"][f"mean_{observation_name}"]

        total_energy_consumption += df["value"].sum()

    return {"energy_consumed_today": int(total_energy_consumption), "unit": "Wh"}


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
        "enlighted.api.run_api:app",
        host="0.0.0.0",
        port=80,
        reload=True,
    )
