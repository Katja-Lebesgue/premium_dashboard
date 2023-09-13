from typing import Callable
from abc import abstractproperty, ABC
import numpy as np
import pandas as pd
from src.utils.interval import MyInterval


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


class CTR(Metric):
    unit = "%"
    num = "clicks"
    denom = "impr"
    interval = MyInterval(0, 1)


class CR(Metric):
    unit = "%"
    num = "purch"
    denom = "clicks"
    interval = MyInterval(0, 1)


class CPM(Metric):
    unit = "$"
    num = "spend_USD"
    denom = "impr"
    scalar = 1000
    interval = MyInterval(0, 1000)


ctr = CTR()
cr = CR()
cpm = CPM()
