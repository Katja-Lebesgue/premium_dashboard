from datetime import date, datetime
from numbers import Number
from typing import Any

from src.utils import *

FRONTEND_NAMES_DICT = {
    "impr": "impressions",
    "n_ads": "number of ads",
    "n_shops": "number of shops",
    "purch": "purchases",
    "purch_value_USD": "purchase value",
    "spend_USD": "ad spend",
    "acquisition": "prospecting",
    "remarketing": "retargeting",
    "year_month": "time period",
}


def get_frontend_name(backend_name: Any) -> str:
    backend_name = convert_enum_to_its_value(backend_name)
    if type(backend_name) in (date, datetime):
        return backend_name.strftime("%Y-%m")

    if isinstance(backend_name, Number) and not isinstance(backend_name, bool):
        return big_number_human_format(num=backend_name)
    return FRONTEND_NAMES_DICT.get(str(backend_name), str(backend_name).replace("_", " "))


def list_to_str(l: list) -> str:
    l = list(map(str, l))
    if len(l) == 0:
        return ""
    if len(l) == 1:
        return l[0]

    return ", ".join(l[:-1]) + " and " + l[-1]


n_days_to_period_dict = {7: "week", 30: "month", 365: "year"}


def n_days_to_period(n_days: int):
    return n_days_to_period_dict.get(n_days, f"{n_days} days")
