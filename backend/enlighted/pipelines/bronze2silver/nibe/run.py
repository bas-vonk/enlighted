import json
import logging
import os
import time

import redis
from enlighted.db import BronzeDbConfig, SilverDbConfig, get_engine, get_session
from enlighted.pipelines.api2bronze.nibe.models import Data
from enlighted.pipelines.bronze2silver.b2s_etl import BaseBronze2SilverETL
from enlighted.pipelines.bronze2silver.models import Base, ValueTimestamp
from redis import Redis
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Nibe Bronze2Silver ETL")


with open(f"{os.path.dirname(__file__)}/mappings.json") as json_file:
    mappings = json.load(json_file)

    parameter_name_per_parameterId = {
        **{
            mapping["parameter_id"]: mapping["enlighted_parameter_name"]
            for mapping in mappings["settings"]
        },
        **{
            mapping["parameter_id"]: mapping["enlighted_parameter_name"]
            for mapping in mappings["system_values"]
        },
        **{
            mapping["parameter_id"]: mapping["enlighted_parameter_name"]
            for mapping in mappings["sensors"]
        },
    }

    mapping_per_parameterId = {
        **{
            mapping["parameter_id"]: mapping["mappings"]
            for mapping in mappings["settings"]
        },
        **{
            mapping["parameter_id"]: mapping["mappings"]
            for mapping in mappings["system_values"]
        },
        **{
            mapping["parameter_id"]: mapping["mappings"]
            for mapping in mappings["sensors"]
        },
    }


class NibeBronze2SilverETL(BaseBronze2SilverETL):
    def __init__(
        self,
        session: Session,
        redis_obj: Redis,
        bronze_table,
        silver_table,
        bronze_table_row_ids_redis_key,
    ):
        self.parameter_name_per_parameterId = parameter_name_per_parameterId
        self.mapping_per_parameterId = mapping_per_parameterId

        BaseBronze2SilverETL.__init__(
            self,
            session=session,
            redis_obj=redis_obj,
            bronze_table=bronze_table,
            silver_table=silver_table,
            bronze_table_row_ids_redis_key=bronze_table_row_ids_redis_key,
        )

    def _get_observation_name(self, row):
        """Get the observation name."""

        return self.parameter_name_per_parameterId[row["parameterId"]]

    def _get_reference(self, row):
        """Build the reference column."""

        reference = str(row["parameterId"])
        if row["designation"]:
            reference += f" | {row['designation']}"

        return reference

    def _get_value(self, row):
        """Get the value from the displayValue and the unit."""

        value = (
            row["displayValue"].replace(row["unit"], "")
            if row["unit"] and row["unit"] in row["displayValue"]
            else row["displayValue"]
        )

        try:
            return float(value)
        except ValueError:
            pass

        try:
            return self.mapping_per_parameterId[row["parameterId"]][row["displayValue"]]
        except KeyError:
            text = f"Value {row['displayValue']} for {row['parameterId']} is missing."
            logger.warning(text)

        return value

    def transform(self, df_bronze):
        """Transform the bronze rows to silver rows."""

        df_silver = df_bronze.copy()
        df_silver["device_brand"] = "nibe"
        df_silver["device_name"] = "f1255pc"

        df_silver["observation_name"] = df_silver.apply(
            lambda row: self._get_observation_name(row), axis=1
        )

        df_silver["observed_at"] = df_silver["created"]
        df_silver["value"] = df_silver.apply(lambda row: self._get_value(row), axis=1)
        df_silver["unit"] = df_silver["unit"]

        df_silver["reference"] = df_silver.apply(
            lambda row: self._get_reference(row), axis=1
        )

        df_silver = df_silver.drop(
            ["id", "parameterId", "title", "displayValue", "designation", "created"],
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
