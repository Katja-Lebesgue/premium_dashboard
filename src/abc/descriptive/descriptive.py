from abc import ABC, abstractproperty

from src.utils import *


class DescriptiveDF(str, Enum):
    done_shop_ids = "done_shop_ids"
    failed_shop_ids = "failed_shop_ids"
    main = "main"
    summary = "summary"


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
    fake_feature = "fake_feature"

    def get_df_path(self, df_type: DescriptiveDF, end_date: date | None = None):
        return os.path.join(self.s3_descriptive_folder, self.tag, f"{end_date}_{df_type}.csv")

    def read_df(self, df_type: DescriptiveDF, end_date: date):
        return read_csv_from_s3(path=self.get_df_path(df_type=df_type, end_date=end_date))

    def get_available_dates(self, df_type: DescriptiveDF) -> list[date]:
        prefix = os.path.join(self.s3_descriptive_folder, self.tag)
        all_objects = list_objects_from_prefix(prefix=prefix)
        list_of_objects = [obj for obj in all_objects if df_type in obj]
        return [to_date(date_str) for date_str in extract_dates_from_str(" ".join(list_of_objects))]
