from abc import ABC, abstractproperty
from typing import Callable
from numbers import Number
from typing import Any

from loguru import logger
import numpy as np
import pandas as pd


from src.utils.interval import MyInterval
from src.utils.converters import big_number_human_format


class Metric(ABC):
    def __str__(self) -> str:
        return type(self).__name__.upper()

    @abstractproperty
    def interval(self) -> MyInterval:
        ...

    @abstractproperty
    def unit(self) -> str:
        ...

    @abstractproperty
    def num(self) -> str:
        ...

    @abstractproperty
    def denom(self) -> str:
        ...

    @property
    def scalar(self) -> float:
        if self.unit == "%":
            return 100
        return 1

    @property
    def formula_df(self):
        return (
            lambda df: self.scalar * df[self.num].sum() / df[self.denom].sum()
            if df[self.denom].sum() > 0
            else np.nan
        )

    @property
    def formula_series(self):
        return lambda s: self.scalar * s[self.num] / s[self.denom] if s[self.denom] > 0 else np.nan

    def format(self, value: Number, big_decimals: int = 2, small_decimals: int = 0):
        formatted_value = big_number_human_format(
            num=value, big_decimals=big_decimals, small_decimals=small_decimals
        )
        if self.unit in ("%",):
            res = f"{formatted_value}{self.unit}"
        else:
            res = f"{self.unit}{formatted_value}"
        return res

    def format_ticker(self, num: Number, pos: Any, small_decimals: int = 2, big_decimals: int = 2) -> str:
        return self.format(value=num, small_decimals=small_decimals, big_decimals=big_decimals)


class CTR(Metric):
    unit = "%"
    num = "clicks"
    denom = "impr"
    interval = MyInterval(0, 100)


class CR(Metric):
    unit = "%"
    num = "purch"
    denom = "clicks"
    interval = MyInterval(0, 100)


class CPM(Metric):
    unit = "$"
    num = "spend_USD"
    denom = "impr"
    scalar = 1000
    interval = MyInterval(0, 1000)


class CAC(Metric):
    unit = "$"
    num = "spend_USD"
    denom = "purch"
    interval = MyInterval(0, 10000)


class ROAS(Metric):
    unit = "%"
    num = "purch_value_USD"
    denom = "spend_USD"
    interval = MyInterval(0, 10000)


ctr = CTR()
cr = CR()
cpm = CPM()
cac = CAC()
roas = ROAS()
