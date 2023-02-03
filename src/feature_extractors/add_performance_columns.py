import pandas as pd
import numpy as np
from currency_converter import CurrencyConverter
from ..s3.read_file_from_s3 import read_json_from_s3
from src.utils.common import convert_to_USD
import json


def add_performance_columns(
    performance: pd.DataFrame,
    conversion_rates_json_path: str = "data/conversion_rates.txt",
) -> pd.DataFrame:

    conversion_rates_json = read_json_from_s3(path=f"conversion_rates.txt")

    performance.fillna(0, inplace=True)
    performance.replace(to_replace="None", value=0, inplace=True)

    performance["ctr"] = performance.apply(lambda df: df.link_clicks / df.impr if df.impr else np.nan, axis=1)
    performance["cr"] = performance.apply(lambda df: df.purch / df.link_clicks if df.link_clicks else np.nan, axis=1)

    performance["roas"] = performance.apply(lambda df: df.purch_value / df.spend if df.spend else np.nan, axis=1)

    int_cols = ["impr", "link_clicks", "purch"]

    float_cols = ["spend"]

    performance[int_cols] = performance[int_cols].astype(int)
    performance[float_cols] = performance[float_cols].astype(float)

    # performance = performance.infer_objects()

    performance["spend_USD"] = performance.apply(
        lambda df: convert_to_USD(
            price=df.spend,
            currency=df.currency,
            conversion_rates_json=conversion_rates_json,
        ),
        axis=1,
    )

    return performance
