import logging
import time
from typing import List

import pandas as pd
from redis import Redis
from sqlalchemy import select
from sqlalchemy.orm import Session

from enlighted.utils import now_hrf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NO_JOB_SLEEP_SECONDS = 1
MAX_BRONZE_ROW_COUNT = 1000


class BaseBronze2SilverETL:
    def __init__(
        self,
        session: Session,
        redis_obj: Redis,
        bronze_table,
        silver_table,
        bronze_table_row_ids_redis_key,
    ):
        self.session = session
        self.redis_obj = redis_obj
        self.bronze_table = bronze_table
        self.silver_table = silver_table
        self.bronze_table_row_ids_redis_key = bronze_table_row_ids_redis_key

    def get_bronze_table_row_ids(self):
        # Obtain all jobs
        return self.redis_obj.rpop(
            self.bronze_table_row_ids_redis_key, MAX_BRONZE_ROW_COUNT
        )

    def extract(self, bronze_ids):
        """Extract data from Bronze layer."""
        query = select(self.bronze_table).where(self.bronze_table.id.in_(bronze_ids))
        with self.session.get_bind(self.bronze_table).connect() as conn:
            return pd.read_sql(query, conn)

    def transform(self, df_bronze: pd.DataFrame) -> pd.DataFrame:
        """Transform the bronze rows to silver rows."""
        raise NotImplementedError

    def load(self, df_silver):
        self.silver_table.upsert(self.session, df_silver.to_dict("records"))
        logger.info(f"Job completed. {len(df_silver)} records ingested.")

    def do_job(self):
        """Do the job: Get rows to process, then ETL them."""
        # logger.info(f"Job started at {now_hrf()}.")

        bronze_table_row_ids: List[int] = self.get_bronze_table_row_ids()
        if not bronze_table_row_ids:
            time.sleep(NO_JOB_SLEEP_SECONDS)
            return

        df_bronze: pd.DataFrame = self.extract(bronze_table_row_ids)

        # No Bronze data
        if df_bronze.empty:
            time.sleep(NO_JOB_SLEEP_SECONDS)
            return

        df_silver: pd.DataFrame = self.transform(df_bronze)
        self.load(df_silver)

    def run(self):
        while True:
            self.do_job()
