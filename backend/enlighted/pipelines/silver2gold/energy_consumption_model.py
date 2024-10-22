import datetime
import functools as ft
import logging
import time
import timeit

import pandas as pd
import statsmodels.api as sm
from scheduler import Scheduler
from sklearn import linear_model
from sqlalchemy.orm import Session

from enlighted.db import GoldDbConfig, SilverDbConfig, get_engine, get_session
from enlighted.pipelines.bronze2silver.models import (
    Event,
    ValueTimestamp,
    ValueTimeWindow,
)
from enlighted.pipelines.silver2gold.models import Base, Insight
from enlighted.pipelines.silver2gold.utils import (
    drop_redundant_columns,
    replace_column_names,
    replace_observed_at_with_window_start_end,
)
from enlighted.utils import now

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.options.display.float_format = "{:.0f}".format

SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = 3600
SECONDS_IN_DAY = 3600 * 24

# Outcome:
# - Verbruik per uur (Envoy production + Tibber consumption - Tibber production)

# Features:
# - Constant
# - All KWH meters
#   - Stove left + stove right
#   - Entertainment station
#   - Dryer
#   - Washing machine
#   - Quooker
#   - Bathroom heater
#   - Raspi cluster
#   - Oven
#   - Fridge-Freezer
#   - Dishwasher
# - Compressor: average frequency during the hour
# - Heat circuit pump: average speed during the hour (0-100%)
# - Brine circuit pump: average speed during the hour (0-100%)


class EnergyConsumptionModel:
    def __init__(self, session):
        self.session = session
        self.now = now()
        self.window_start_lower_bound = self.now - (60 * 60 * 24 * 365)

        self.device_names = [
            "stove_left",
            "stove_right",
            "quooker",
            "heat_recovery_ventilation",
            "dryer",
            "washing_machine",
            "raspi_cluster",
            "bathroom_heater",
            "entertainment_station",
            "oven",
            "dishwasher",
            "fridge_freezer",
        ]

        self.heat_pump_observation_names = [
            "compressor_frequency",
            "heat_circuit_pump_speed",
            "brine_circuit_pump_speed",
        ]

        self.window_cols = ["window_start", "window_end"]

    def _get_value_time_window(self, device_name, observation_name):
        return pd.DataFrame.from_records(
            ValueTimeWindow.read(
                session=self.session,
                device_name=device_name,
                observation_name=observation_name,
                window_start_lower_bound=self.window_start_lower_bound,
            )
        )

    def _get_value_timestamp(
        self, device_name, observation_name, top_of_the_hour_only=False
    ):
        return pd.DataFrame.from_records(
            ValueTimestamp.read(
                session=self.session,
                device_name=device_name,
                observation_name=observation_name,
                observed_at_lower_bound=self.window_start_lower_bound,
                top_of_the_hour_only=top_of_the_hour_only,
            )
        )

    def _get_heat_pump_observation_dataframe(self, observation_name):
        df = self._get_value_timestamp("f1255pc", observation_name)
        drop_redundant_columns(df, ["value", "observed_at"])
        replace_observed_at_with_window_start_end(df, SECONDS_IN_HOUR)
        df = df.groupby(self.window_cols).mean()
        replace_column_names(df, {"value": f"mean_{observation_name}"})

        return df

    def _get_smart_meter_observation_dataframe(self, observation_name, column_name):
        df = self._get_value_time_window("pulse", observation_name)
        drop_redundant_columns(df, self.window_cols + ["value"])
        replace_column_names(df, {"value": column_name})
        df[column_name] = df[column_name] * 1000

        return df

    def _get_df_energy_sold(self):
        df = self._get_value_time_window("pulse", "electricity_sold_to_the_grid")
        drop_redundant_columns(df, self.window_cols + ["value"])
        replace_column_names(df, {"value": "energy_sold"})
        df["energy_sold"] = df["energy_sold"] * 1000

        return df

    def _get_df_energy_purchased(self):
        df = self._get_value_time_window("pulse", "electricity_purchased_from_the_grid")
        drop_redundant_columns(df, self.window_cols + ["value"])
        replace_column_names(df, {"value": "energy_purchased"})
        df["energy_purchased"] = df["energy_purchased"] * 1000

        return df

    def _get_df_energy_produced(self):
        df = self._get_value_timestamp("envoy", "current_production")
        drop_redundant_columns(df, columns_to_keep=["value", "observed_at"])
        replace_column_names(df, {"value": "energy_produced"})
        replace_observed_at_with_window_start_end(df, interval_seconds=SECONDS_IN_HOUR)
        df = df.groupby(self.window_cols).mean()

        return df

    def _get_df_energy_usage_for_device(self, device_name):
        df = self._get_value_timestamp(device_name, "total_energy_used", True)
        drop_redundant_columns(df, columns_to_keep=["observed_at", "value"])
        df.sort_values(by=["observed_at"], inplace=True)
        replace_column_names(df, {"observed_at": "window_end"})
        df["window_start"] = df["window_end"] - SECONDS_IN_HOUR
        df[device_name] = df["value"].diff()
        df[device_name] = df[device_name] * 1000
        df.drop(columns=["value"], inplace=True)
        df = df[df["window_start"].diff() == SECONDS_IN_HOUR]

        return df

    def _merge_on_window_cols(self, df1, df2):
        return pd.merge(df1, df2, how="left", on=self.window_cols)

    def run(self):
        """Make the model."""

        start = timeit.default_timer()

        # Get the dataframes with energy sold, purchased, and produced
        df_energy_sold = self._get_df_energy_sold()
        df_energy_purchased = self._get_df_energy_purchased()
        df_energy_produced = self._get_df_energy_produced()

        # Prepare first merged dataframe
        dfs = [df_energy_sold, df_energy_purchased, df_energy_produced]
        df = ft.reduce(lambda left, right: self._merge_on_window_cols(left, right), dfs)

        # Compute energy used in the house
        df["energy_used"] = df["energy_purchased"]
        df["energy_used"] = df["energy_used"] + df["energy_produced"]
        df["energy_used"] = df["energy_used"] - df["energy_sold"]

        # Add energy usage for devices measured with a kWh meter
        for device_name in self.device_names:
            df_device = self._get_df_energy_usage_for_device(device_name=device_name)
            df = self._merge_on_window_cols(df, df_device)

        # Create an energy_used_unknown column by taking energy used and substracting
        # all devices that are measured using a kWh meter
        df["energy_used_unknown"] = df["energy_used"]
        for device_name in self.device_names:
            df["energy_used_unknown"] = df["energy_used_unknown"] - df[device_name]

        # Combine the two sides of the stove into one stove
        df["stove"] = df["stove_left"] + df["stove_right"]
        df.drop(columns=["stove_left", "stove_right"], inplace=True)

        # Add heat pump activity data
        for observation_name in self.heat_pump_observation_names:
            df_device = self._get_heat_pump_observation_dataframe(observation_name)
            df = self._merge_on_window_cols(df, df_device)

        df.dropna(subset=["energy_used_unknown"], inplace=True)

        try:
            y = df["energy_used_unknown"]
            x = df[
                [
                    f"mean_{observation_name}"
                    for observation_name in self.heat_pump_observation_names
                ]
            ].fillna(0)

            reg = linear_model.LinearRegression()
            reg.fit(x, y)

            insight = {
                "constant": reg.intercept_,
                "coefficients": dict(zip(x.columns, reg.coef_)),
                "r_squared": reg.score(x, y),
            }

            Insight.upsert(
                session,
                {
                    "insight_name": "energy_consumption_model",
                    "insight": insight,
                    "observed_at": self.now,
                },
            )

            # For inspection purposes only
            x = sm.add_constant(x)
            model = sm.OLS(y, x).fit()
            print(model.summary())

        except ValueError:
            logger.warning("Not enough data to make a model.")

        print(f"One run took: {timeit.default_timer() - start} seconds.")


if __name__ == "__main__":
    # Databases
    engine = get_engine(GoldDbConfig())
    session = get_session(
        {
            ValueTimestamp: SilverDbConfig(),
            ValueTimeWindow: SilverDbConfig(),
            Event: SilverDbConfig(),
            Insight: GoldDbConfig(),
        }
    )

    """Ensure all tables exist."""
    Base.metadata.create_all(engine)

    # Create the model object
    energy_consumption_model = EnergyConsumptionModel(session=session)

    # Always run once upon startup
    energy_consumption_model.run()

    # Create the scheduler
    schedule = Scheduler()
    schedule.hourly(
        datetime.time(minute=0),
        lambda: energy_consumption_model.run(),
    )

    while True:
        schedule.exec_jobs()
        time.sleep(60)
