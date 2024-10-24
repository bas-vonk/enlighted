import logging
import time

import pandas as pd
from sqlalchemy.orm import Session

from enlighted.db import GoldDbConfig, SilverDbConfig, get_engine, get_session
from enlighted.pipelines.bronze2silver.models import ValueTimestamp
from enlighted.pipelines.silver2gold.models import Base, Insight
from enlighted.utils import now

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("S2G: Heat pump operating hours prices")

spa_labels = {0.0: "Unknown", 1.0: "Cheap", 2.0: "Average", 3.0: "Expensive"}


def get_insight(df):
    result_dict = (
        (df.groupby(["spa_price_level"]).count() / len(df) * 100).round(0).to_dict()
    )
    return result_dict["system_status"]


def job(session: Session):
    ts_now = now()
    sixty_days_ago = ts_now - (60 * 60 * 24 * 60)
    seven_days_ago = ts_now - (60 * 60 * 24 * 7)

    device_name = "f1255pc"

    # Get the data of the heat pump status
    observation_name = "system_status"
    df_system_status = pd.DataFrame.from_records(
        ValueTimestamp.read(
            session=session,
            device_name=device_name,
            observation_name=observation_name,
            observed_at_lower_bound=sixty_days_ago,
        )
    ).rename(columns={"value": observation_name})

    # Get the data of the SPA price levels
    observation_name = "spa_price_level"
    df_spa = pd.DataFrame.from_records(
        ValueTimestamp.read(
            session=session,
            device_name=device_name,
            observation_name=observation_name,
            observed_at_lower_bound=sixty_days_ago,
        )
    ).rename(columns={"value": observation_name})

    df_spa["spa_price_level"] = df_spa.apply(
        lambda row: spa_labels[row["spa_price_level"]], axis=1
    )

    # Join and select the relevant columns
    df_system_status.drop(
        columns=[
            "id",
            "created_at",
            "device_brand",
            "device_name",
            "observation_name",
            "reference",
            "unit",
            "top_of_the_hour",
        ],
        inplace=True,
    )
    df_spa.drop(
        columns=[
            "id",
            "created_at",
            "device_brand",
            "device_name",
            "observation_name",
            "reference",
            "unit",
            "top_of_the_hour",
        ],
        inplace=True,
    )
    df = df_system_status.join(df_spa.set_index("observed_at"), on="observed_at")
    df = df[(df["system_status"] == 1) | (df["system_status"] == 2)]
    df = df.dropna()

    insight = {
        "last_sixty_days": get_insight(df),
        "last_seven_days": get_insight(df[df["observed_at"] >= seven_days_ago]),
    }

    Insight.upsert(
        session,
        {
            "insight_name": "heat_pump_operating_hours_prices",
            "insight": insight,
            "observed_at": int(df["observed_at"].max()),
        },
    )


if __name__ == "__main__":
    # Databases
    engine = get_engine(GoldDbConfig())
    session = get_session({ValueTimestamp: SilverDbConfig(), Insight: GoldDbConfig()})

    """Ensure all tables exist."""
    Base.metadata.create_all(engine)

    while True:
        job(session)
        time.sleep(300)
