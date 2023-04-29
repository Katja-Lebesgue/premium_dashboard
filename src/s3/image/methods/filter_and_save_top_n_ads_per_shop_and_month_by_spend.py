from datetime import date, datetime

import pandas as pd

from src.database.session import SessionLocal
from src.image_analysis.utils import *
from src.models import *
from src.utils import *

db = SessionLocal()


def filter_and_save_top_n_ads_per_shop_and_month_by_spend(
    self,
    end_date: date = date.today(),
    start_date: date = datetime.strptime("2015-01-01", "%Y-%m-%d").date(),
):
    table_path = self.top_n_ads_per_shop_and_month_by_spend
    performance_df = read_csv_from_s3(self.url_performance_df)
    # neither url is used by more than one shop
    assert (performance_df.groupby("url").apply(lambda df: df.shop_id.nunique()) > 1).sum() == 0
    performance_df["year_month_date"] = performance_df.year_month.apply(
        lambda x: datetime.strptime(x, "%Y-%m")
    ).dt.date
    performance_df = performance_df[
        (performance_df.year_month_date >= start_date) & (performance_df.year_month_date <= end_date)
    ]
    performance_df.drop(columns=["year_month_date"], inplace=True)

    top_ads = (
        performance_df.groupby(["shop_id", "year_month"])
        .apply(lambda df: df.sort_values("spend_USD").tail(self.n_ads_per_shop_and_month))
        .reset_index(drop=True)
    )

    save_csv_to_s3(top_ads, path=table_path, index=False)
