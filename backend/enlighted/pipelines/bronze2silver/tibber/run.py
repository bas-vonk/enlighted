import argparse
import json
import os
import time

import pandas as pd
import redis
from redis import Redis
from sqlalchemy.orm import Session

from enlighted.db import BronzeDbConfig, SilverDbConfig, get_engine, get_session
from enlighted.pipelines.api2bronze.tibber.models import (
    Consumption,
    LiveMeasurement,
    Production,
)
from enlighted.pipelines.bronze2silver.b2s_etl import BaseBronze2SilverETL
from enlighted.pipelines.bronze2silver.models import Base, ValueTimeWindow


class TibberBronze2SilverETL(BaseBronze2SilverETL):
    def __init__(
        self,
        session: Session,
        redis_obj: Redis,
        bronze_table,
        silver_table,
        bronze_table_row_ids_redis_key,
        mappings_filename,
    ):
        with open(f"{os.path.dirname(__file__)}/{mappings_filename}") as json_file:
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
        df_silver.drop(
            self.mappings["columns_to_drop_at_the_beginning"], axis=1, inplace=True
        )

        # Unpivot the dataframe. Put all columns with values in their own row
        df_silver = pd.melt(
            df_silver,
            id_vars=self.mappings["id_columns"],
            value_vars=self.mappings["value_columns"],
        )

        # The 'melt' function adds the 'variable' column, which contains the
        # name of the observation
        df_silver = df_silver.rename(
            columns={
                **self.mappings["columns_to_rename"],
                **{"variable": "observation_name"},
            }
        )

        # Rename the parameters
        df_silver["observation_name"] = df_silver.apply(
            lambda row: self.mappings["parameter_names"][row["observation_name"]],
            axis=1,
        )

        # Add the units
        df_silver["unit"] = df_silver.apply(
            lambda row: self.mappings["units"][row["observation_name"]], axis=1
        )

        # Add the device name and brand (and the empty reference)
        df_silver["device_brand"] = self.mappings["device_brand"]
        df_silver["device_name"] = self.mappings["device_name"]

        # Drop last columns
        df_silver.drop(
            self.mappings["columns_to_drop_at_the_end"], axis=1, inplace=True
        )
        return df_silver


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "bronze_table", choices=["production", "consumption", "live_measurements"]
    )
    args = parser.parse_args()

    # Databases
    engine = get_engine(SilverDbConfig())
    session = get_session(
        {
            ValueTimeWindow: SilverDbConfig(),
            Production: BronzeDbConfig(),
            Consumption: BronzeDbConfig(),
            LiveMeasurement: BronzeDbConfig(),
        }
    )

    # Redis
    redis_obj = redis.Redis(host="192.168.2.201", port=6379, decode_responses=True)

    # Ensure all tables exist
    Base.metadata.create_all(engine)

    # Set up the right ETL, based on the passed argument
    if args.bronze_table == "production":
        bronze_table = Production
        silver_table = ValueTimeWindow
        bronze_table_row_ids_redis_key = "tibber.Production"
        mappings_filename = "mappings_production.json"
    elif args.bronze_table == "consumption":
        bronze_table = Consumption
        silver_table = ValueTimeWindow
        bronze_table_row_ids_redis_key = "tibber.Consumption"
        mappings_filename = "mappings_consumption.json"
    else:
        raise ValueError('Only "consumption" or "production" allowed.')

    while True:
        TibberBronze2SilverETL(
            session=session,
            redis_obj=redis_obj,
            bronze_table=bronze_table,
            silver_table=silver_table,
            bronze_table_row_ids_redis_key=bronze_table_row_ids_redis_key,
            mappings_filename=mappings_filename,
        ).run()
        time.sleep(1)
