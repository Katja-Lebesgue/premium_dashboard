from abc import ABC, abstractproperty

from src.utils import *


class Descriptive(ABC):
    @abstractproperty
    def descriptive_columns(self) -> list[str]:
        ...

    @abstractproperty
    def tag(self) -> str:
        ...

    s3_descriptive_folder = "descriptive"

    metric_columns = [
        "spend_USD",
        "impr",
        "clicks",
        "purch",
        "purch_value_USD",
        "n_ads",
    ]

    explode_descriptive_columns = []
    fake_column_for_total_sum_name = "fake_column_for_total_sum"
