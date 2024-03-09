import json
import os
import time

import redis
from enlighted.db import BronzeDbConfig, SilverDbConfig, get_engine, get_session
from enlighted.pipelines.api2bronze.homeconnect.models import OperationState
from enlighted.pipelines.bronze2silver.b2s_etl import BaseBronze2SilverETL
from enlighted.pipelines.bronze2silver.models import Base, Event
from redis import Redis
from sqlalchemy.orm import Session


class HomeConnectBronze2SilverETL(BaseBronze2SilverETL):
    def __init__(
        self,
        session: Session,
        redis_obj: Redis,
        bronze_table,
        silver_table,
        bronze_table_row_ids_redis_key,
    ):
        with open(f"{os.path.dirname(__file__)}/mappings.json") as json_file:
            self.mappings = json.load(json_file)

        BaseBronze2SilverETL.__init__(
            self,
            session=session,
            redis_obj=redis_obj,
            bronze_table=bronze_table,
            silver_table=silver_table,
            bronze_table_row_ids_redis_key=bronze_table_row_ids_redis_key,
        )

    def transform(self, df_bronze):
        """Transform the bronze rows to silver rows."""

        df_silver = df_bronze.copy()

        # Drop the columns that are not needed for the transformation
        df_silver.drop(self.mappings["columns_to_drop"], axis=1, inplace=True)

        # Rename certain columns
        df_silver = df_silver.rename(columns=self.mappings["columns_to_rename"])

        # Map the event to a proper name
        df_silver["event"] = df_silver.apply(
            lambda row: self.mappings["parameter_values"][row["event"]], axis=1
        )

        # Add the device name and brand
        df_silver["device_brand"] = "siemens"
        df_silver["device_name"] = df_silver.apply(
            lambda row: self.mappings["haId_to_device_name"][row["haId"]], axis=1
        )

        # Drop columns that are no longer necessary after processing
        df_silver.drop(["haId", "key"], axis=1, inplace=True)

        return df_silver


if __name__ == "__main__":
    engine = get_engine(SilverDbConfig())
    session = get_session({Event: SilverDbConfig(), OperationState: BronzeDbConfig()})

    redis_obj = redis.Redis(host="192.168.2.201", port=6379, decode_responses=True)

    # Create all silver tables
    Base.metadata.create_all(engine)

    while True:
        HomeConnectBronze2SilverETL(
            session=session,
            redis_obj=redis_obj,
            bronze_table=OperationState,
            silver_table=Event,
            bronze_table_row_ids_redis_key="homeconnect.OperationState",
        ).run()
        time.sleep(1)
