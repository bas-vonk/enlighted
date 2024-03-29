import json
import os
import time

import pandas as pd
import redis
from enlighted.db import BronzeDbConfig, SilverDbConfig, get_engine, get_session
from enlighted.pipelines.api2bronze.homewizard.models import Measurement
from enlighted.pipelines.bronze2silver.b2s_etl import BaseBronze2SilverETL
from enlighted.pipelines.bronze2silver.models import Base, ValueTimestamp
from redis import Redis
from sqlalchemy.orm import Session


class HomeWizardBronze2SilverETL(BaseBronze2SilverETL):
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

        df_silver["top_of_the_hour"] = df_silver.apply(
            lambda row: row["observed_at"] % 3600 == 0, axis=1
        )

        # Add the device brand
        df_silver["device_brand"] = self.mappings["device_brand"]

        return df_silver


if __name__ == "__main__":
    engine = get_engine(SilverDbConfig())
    session = get_session(
        {ValueTimestamp: SilverDbConfig(), Measurement: BronzeDbConfig()}
    )

    redis_obj = redis.Redis(host="192.168.2.201", port=6379, decode_responses=True)

    # Create all silver tables
    Base.metadata.create_all(engine)

    while True:
        HomeWizardBronze2SilverETL(
            session=session,
            redis_obj=redis_obj,
            bronze_table=Measurement,
            silver_table=ValueTimestamp,
            bronze_table_row_ids_redis_key="homewizard.Measurement",
        ).run()
        time.sleep(1)
