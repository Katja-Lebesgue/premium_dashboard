import streamlit as st
import pandas as pd
import numpy as np
from src.pingers import ping_ads_insights_all_platforms
from src.database.session import db
from src.utils.common import get_all_subsets
from src.utils.enum import get_enum_values
from src.models.enums.EPlatform import EPlatform


def all_platforms():
    df = ping_ads_insights_all_platforms(db=db)

    platforms = get_enum_values(EPlatform)
    platform_combinations = get_all_subsets(platforms)

    table = pd.DataFrame(columns=["combination", "shops", "budget_split"])

    for combination in platform_combinations:
        if not len(combination):
            continue
        row = get_data_by_platform_combination(df=df, combination=combination, platforms=platforms)
        table.loc[len(table), :] = row

    st.dataframe(table)


def get_spend_ratio(s: pd.Series, platforms: list):
    ratio = [s[f"{platform}_spend"] / s.full_spend for platform in platforms]
    return ratio


def get_data_by_platform_combination(df: pd.DataFrame, combination: list, platforms: list):
    filter = [True in range(len(df))]
    for platform in platforms:
        if platform in combination:
            filter = filter & (df[f"{platform}_spend"].notna())
        else:
            filter = filter & (df[f"{platform}_spend"].isna())
    filtered = df[filter].copy()
    filtered["full_spend"] = filtered.apply(
        lambda df: sum([df[f"{platform}_spend"] for platform in combination]), axis=1
    )
    platforms_without_the_last_one = combination[: len(combination) - 1]
    filtered["spend_ratio"] = filtered.apply(
        lambda df: get_spend_ratio(df, platforms=platforms_without_the_last_one), axis=1
    )
    mean_ratio = np.mean(filtered["spend_ratio"].tolist(), axis=0)
    print(mean_ratio)
    result = {
        "combination": "_".join(combination),
        "shops": len(filtered) / len(df),
        "budget_split": list(mean_ratio) + [1 - mean_ratio.sum()],
    }
    return result
