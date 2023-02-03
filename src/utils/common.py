import sys
from time import strftime

sys.path.append("./.")

import os
from dotenv import load_dotenv

load_dotenv()

import ast
import pandas as pd
from src.types import types
import numpy as np
from currency_converter import CurrencyConverter
import math
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from metadata.globals import *


def read_csv_and_eval(path: str) -> pd.DataFrame:

    # reads csv using pd.read_csv and then uses ast.literal_eval() to evaluate all columns in df.

    df = pd.read_csv(path, dtype=column_dtypes)

    str_cols = [col for col, type in column_dtypes.items() if type == str]

    cols_to_eval = list(set(df.columns) - set(str_cols))

    df.loc[:, cols_to_eval] = df.loc[:, cols_to_eval].applymap(eval_but_leave_string_if_you_cant)

    df = df.infer_objects()

    return df


def eval_but_leave_string_if_you_cant(text: str):

    try:
        out = ast.literal_eval(text)
    except:
        out = text

    return out


def separate_thousands_and_round(num: float | int | str, r: int = 2) -> str:
    if type(num) == str:
        num = float(num)
    num = round(num, r)
    return f"{num:,}".replace(",", " ")


def nan_to_none(num):

    if np.isnan(num) or math.isinf(num):
        return None
    else:
        return num


def big_number_human_format(num, big_decimals: int = 2, small_decimals: int = 0):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0

    if magnitude:
        num_format = f"%.{big_decimals}f%s" % (
            num,
            ["", "K", "M", "G", "T", "P"][magnitude],
        )
    else:
        num_format = f"%.{small_decimals}f%s" % (
            num,
            ["", "K", "M", "G", "T", "P"][magnitude],
        )

    return num_format


def convert_to_USD(price: float | int, currency: str, conversion_rates_json: str) -> float:

    if type(currency) != str or currency not in conversion_rates_json.keys():
        return None
    return price / conversion_rates_json[currency]


def element_to_list(a):
    if type(a) != list:
        a = [a]

    return list(a)


def list_to_series(x):
    if type(x) == list:
        return pd.Series(x)

    return x


def none_to_unknown(a):
    if a is None or a == "None":
        return "unknown"
    return a


def get_range_of_months(
    start_date: str,
    end_date: str = date.today().strftime("%Y-%m-%d"),
    return_dates=False,
):

    start_date, end_date = (to_date(x) for x in (start_date, end_date))

    dates_list = []
    last_added = start_date
    while last_added <= end_date:
        dates_list.append(last_added)
        last_added = last_added + relativedelta(months=1)

    if return_dates is False:
        dates_list = [d.strftime("%Y-%-m") for d in dates_list]

    return dates_list


def to_date(x):
    if type(x) == str:
        x = datetime.strptime(x, "%Y-%m-%d").date()
    if type(x) == datetime:
        x = x.date()
    return x


def add_global_s3_folder(path):
    return f"{os.getenv('S3_PATH')}/{path}"


def remove_any(s: str, underscore_to_space: bool = True):

    if underscore_to_space:
        s = s.replace("_", " ")

    s = s.removesuffix("_any")
    s = s.removesuffix(" any")
    return s
