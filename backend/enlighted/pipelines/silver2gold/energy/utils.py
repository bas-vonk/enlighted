import numpy as np

HOURS_IN_DAY = 24
SECONDS_IN_DAY = 24 * 3600
MINIMAL_REST_PERCENTAGE = 0.1


def energy_used_in_rest(power_usage_in_rest, energy_used_total):
    return min(power_usage_in_rest * HOURS_IN_DAY, energy_used_total)


def calculate_power_usage_in_rest(power_measurements):
    return power_measurements.quantile(MINIMAL_REST_PERCENTAGE)


def calculate_current_power_usage(power_measurements):
    return np.mean(power_measurements.tail(5))


def calculate_energy_used_total_using_measurements(power_measurements, hours_in_window):
    return np.mean(power_measurements) * hours_in_window


def calculate_energy_used_total_using_kwh_values(kwh_values):
    return (max(kwh_values) - min(kwh_values)) * 1000


def replace_observed_at_with_window_start_end(df, interval_seconds=SECONDS_IN_DAY):
    # Add window_start
    df.loc[:, "window_start"] = df.apply(
        lambda row: row["observed_at"] - (row["observed_at"] % interval_seconds),
        axis=1,
    )

    # Add window_end
    df.loc[:, "window_end"] = df.apply(
        lambda row: row["window_start"] + interval_seconds, axis=1
    )

    # Drop observed_at
    df.drop(columns=["observed_at"], inplace=True)


def replace_column_names(df, column_names_mappings):
    df.rename(columns=column_names_mappings, inplace=True)


def drop_redundant_columns(df, columns_to_keep):
    columns_to_drop = [column for column in df.columns if column not in columns_to_keep]
    df.drop(columns=columns_to_drop, inplace=True)
