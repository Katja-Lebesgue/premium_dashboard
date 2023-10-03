from enum import Enum


class Period(str, Enum):
    date = "date"
    year_month = "year_month"
    all = "all"
