import argparse
import time

import redis
from enlighted.db import BronzeDbConfig, SilverDbConfig, get_engine, get_session
from enlighted.pipelines.api2bronze.netatmo.models import (
    IndoorMeasurement,
    OutdoorMeasurement,
)
from enlighted.pipelines.bronze2silver.b2s_etl import BaseBronze2SilverETL
from enlighted.pipelines.bronze2silver.models import Base, ValueTimestamp
from redis import Redis
from sqlalchemy.orm import Session


class NetatmoBronze2SilverETL(BaseBronze2SilverETL):
    def __init__(
        self,
        session: Session,
        redis_obj: Redis,
        bronze_table,
        silver_table,
        bronze_table_row_ids_redis_key,
        device_name,
    ):
        BaseBronze2SilverETL.__init__(
            self,
            session=session,
            redis_obj=redis_obj,
            bronze_table=bronze_table,
            silver_table=silver_table,
            bronze_table_row_ids_redis_key=bronze_table_row_ids_redis_key,
        )

        self.device_name = device_name

    def transform(self, df_bronze):
        """Transform the bronze rows to silver rows."""

        df_silver = df_bronze.copy()

        # Format the right columns
        df_silver.drop(["id", "created"], axis=1, inplace=True)
        df_silver.rename(
            columns={"ts": "observed_at", "parameter_name": "observation_name"},
            inplace=True,
        )

        # Drop the amount_of_stations for outdoor columns
        if bronze_table == OutdoorMeasurement:
            df_silver.drop(["amount_of_stations"], axis=1, inplace=True)

        # Set the device
        df_silver["device_brand"] = "netatmo"
        df_silver["device_name"] = self.device_name

        return df_silver


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "bronze_table", choices=["indoor_measurements", "outdoor_measurements"]
    )
    args = parser.parse_args()

    # Databases
    engine = get_engine(SilverDbConfig())
    session = get_session(
        {
            ValueTimestamp: SilverDbConfig(),
            IndoorMeasurement: BronzeDbConfig(),
            OutdoorMeasurement: BronzeDbConfig(),
        }
    )

    # Redis
    redis_obj = redis.Redis(host="192.168.2.201", port=6379, decode_responses=True)

    # Ensure all tables exist
    Base.metadata.create_all(engine)

    # Set up the right ETL, based on the passed argument
    if args.bronze_table == "indoor_measurements":
        bronze_table = IndoorMeasurement
        bronze_table_row_ids_redis_key = "netatmo.IndoorMeasurement"
        device_name = "main_station"
    elif args.bronze_table == "outdoor_measurements":
        bronze_table = OutdoorMeasurement
        bronze_table_row_ids_redis_key = "netatmo.OutdoorMeasurement"
        device_name = "outdoor_module"
    else:
        raise ValueError(
            'Only "indoor_measurements" or "outdoor_measurements" allowed.'
        )

    while True:
        NetatmoBronze2SilverETL(
            session=session,
            redis_obj=redis_obj,
            bronze_table=bronze_table,
            silver_table=ValueTimestamp,
            bronze_table_row_ids_redis_key=bronze_table_row_ids_redis_key,
            device_name=device_name,
        ).run()
        time.sleep(1)
