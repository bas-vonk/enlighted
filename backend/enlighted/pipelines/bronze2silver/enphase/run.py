import datetime
import logging
from time import sleep

import pandas as pd
import redis
from scheduler import Scheduler  # type: ignore
from sqlalchemy.engine import Engine

from enlighted.db import get_engine
from enlighted.pipelines.bronze2silver.models import Base, Data
from enlighted.utils import now_hrf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Enphase Envoy ETL")


class EnphaseB2S:
    def __init__(
        self,
        source_engine: Engine,
        source_table: str,
        target_engine: Engine,
    ):
        self.source_engine = source_engine
        self.source_table = source_table

        self.target_engine = target_engine

    def extract(self, source_row_ids):
        with self.source_engine.connect() as conn:
            return pd.read_sql(
                f"SELECT * FROM {self.source_table} "
                f"WHERE id IN ({','.join(source_row_ids)})",
                conn,
            )

    def transform(self, df_extracted):
        df_watt_now = pd.DataFrame()
        df_watt_now["value"] = df_extracted["wNow"]
        df_watt_now["observed_at"] = df_extracted["readingTime"]
        df_watt_now["observation_name"] = "solar_production_now"
        df_watt_now["unit"] = "watt"

        df_active_inverters = pd.DataFrame()
        df_active_inverters["value"] = df_extracted["activeCount"]
        df_active_inverters["observed_at"] = df_extracted["readingTime"]
        df_active_inverters["observation_name"] = "active_inverter_count"
        df_active_inverters["unit"] = ""

        df_transformed = pd.concat(
            [df_watt_now, df_active_inverters], ignore_index=True
        )

        df_transformed["device_brand"] = "enphase"
        df_transformed["device_name"] = "envoy"

        return df_transformed

    def load(self, df_transformed):
        Data.upsert(self.target_engine, df_transformed.to_dict("records"))

    def do_job(self, source_ids):
        df_extracted = self.extract(source_ids)
        df_transformed = self.transform(df_extracted)
        self.load(df_transformed)

    def run(self) -> None:
        """Run the ETL."""

        # Get Redis
        redis_obj = redis.Redis(host="192.168.2.202", port=6379, decode_responses=True)

        while True:
            source_row_ids = redis_obj.rpop("tibber.Production", 1000)

            if source_row_ids is None:
                return

            # Remove duplicates
            source_row_ids = list(set(source_row_ids))

            self.do_job(source_row_ids)
            logger.info(
                f"Run completed at {now_hrf()}. {len(source_row_ids)} records processed."
            )


if __name__ == "__main__":
    # Get an engine for the source
    source_engine = get_engine(
        "username",
        "password",
        "192.168.2.202",
        "1_bronze",
        "5432",
    )

    # Get an engine for the targer
    target_engine = get_engine(
        "username",
        "password",
        "192.168.2.202",
        "2_silver",
        "5432",
    )

    """Ensure the silver database layer exists."""
    Base.metadata.create_all(target_engine)

    schedule = Scheduler()
    schedule.cyclic(
        datetime.timedelta(seconds=5),
        lambda: EnphaseB2S(
            source_engine, "enphase_envoy.production", target_engine
        ).run(),
    )

    while True:
        schedule.exec_jobs()
        sleep(1)
