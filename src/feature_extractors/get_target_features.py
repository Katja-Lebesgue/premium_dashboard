import sys

sys.path.append("./.")

import pandas as pd
import numpy as np
from multiset import *


def get_target_features(df: pd.DataFrame) -> pd.DataFrame:

    if len(df) == 0:
        return df

    df.countries = df.countries.apply(
        lambda countries: [country.upper() for country in countries]
        if type(countries) == list
        else None
    )

    age_range = (
        lambda df: df.age_max - df.age_min
        if df.age_max is not None
        and df.age_min is not None
        and not np.isnan(df.age_max)
        and not np.isnan(df.age_min)
        else 100
    )

    df["age_range"] = df.apply(age_range, axis=1)

    df["number_of_custom_audiences"] = df.custom_audiences.apply(
        lambda x: len(x) if x is not None else 0
    )

    df["targets_US"] = df.countries.apply(targets_US)
    df["targets_english"] = df.countries.apply(targets_english)

    df["number_of_countries"] = df.countries.apply(
        lambda countries: len(countries) if countries is not None else 0
    )

    return df


def targets_US(countries: list) -> bool:
    if type(countries) is not list:
        return False

    return "US" in countries


def targets_english(countries: list) -> bool:
    if type(countries) is not list:
        return False
    return any([country in countries for country in ["US", "AU", "GB", "CA", "CAN"]])


def main():
    print(targets_english(["konj"]))
    return


if __name__ == "__main__":
    main()
