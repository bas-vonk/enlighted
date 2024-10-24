import logging
import time
from pprint import pprint

import pandas as pd
import redis
from enlighted.db import BronzeDbConfig, SilverDbConfig, get_engine, get_session
from enlighted.pipelines.api2bronze.nibe.models import Data
from enlighted.pipelines.bronze2silver.b2s_etl import BaseBronze2SilverETL
from enlighted.pipelines.bronze2silver.models import Base, ValueTimestamp
from enlighted.pipelines.bronze2silver.nibe.config import NibeB2SConfig
from redis import Redis
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Nibe Bronze2Silver ETL")

parameters = NibeB2SConfig().parameters


class NibeBronze2SilverETL(BaseBronze2SilverETL):
    def __init__(
        self,
        session: Session,
        redis_obj: Redis,
        bronze_table,
        silver_table,
        bronze_table_row_ids_redis_key,
    ):

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

        # Drop all parameters that are not mapped (and hence we don't want in Silver)
        df_silver = df_silver[df_silver["parameterId"].isin(parameters.keys())]

        # If nothing is left, return an empty dataframe
        if df_silver.empty:
            return df_silver

        # Set the device information
        df_silver["device_brand"] = "nibe"
        df_silver["device_name"] = "f1255pc"

        # Set the proper observation name based on the mappings
        df_silver["observation_name"] = df_silver.apply(
            lambda row: parameters.get(row["parameterId"])["silver_parameter_name"],
            axis=1,
        )

        # Rename columns to fit the silver data model
        df_silver.rename(
            columns={
                "parameterUnit": "unit",
                "created": "observed_at",
                "parameterId": "reference",
            },
            inplace=True,
        )

        # Drop the now redundant columns
        df_silver = df_silver.drop(
            ["id", "parameterName", "strVal", "timestamp"],
            axis=1,
        )

        return df_silver


if __name__ == "__main__":
    # Databases
    engine = get_engine(SilverDbConfig())
    session = get_session({ValueTimestamp: SilverDbConfig(), Data: BronzeDbConfig()})

    # Redis
    redis_obj = redis.Redis(host="192.168.2.201", port=6379, decode_responses=True)

    # Ensure all tables exist
    Base.metadata.create_all(engine)

    while True:
        NibeBronze2SilverETL(
            session=session,
            redis_obj=redis_obj,
            bronze_table=Data,
            silver_table=ValueTimestamp,
            bronze_table_row_ids_redis_key="nibe.Data",
        ).run()
        time.sleep(1)
