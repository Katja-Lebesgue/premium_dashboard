from abc import ABC, abstractproperty

from src.utils import *


class Descriptive(ABC):
    @abstractproperty
    def descriptive_columns(self) -> list[str]:
        ...

    @abstractproperty
    def tag(self) -> str:
        ...

    metric_columns = [
        "spend_USD",
        "impr",
        "clicks",
        "purch",
        "purch_value_USD",
        "n_ads",
    ]
