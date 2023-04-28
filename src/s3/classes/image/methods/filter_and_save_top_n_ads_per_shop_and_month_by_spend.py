from datetime import date, datetime

import pandas as pd

from src.database.session import SessionLocal
from src.image_analysis.utils import *
from src.models import *
from src.s3.utils import read_csv_from_s3, save_csv_to_s3

db = SessionLocal()


def filter_and_save_top_n_ads_per_shop_and_month_by_spend(
    self,
    n_ads_per_shop: int = 5,
    start_date: date | None = None,
    end_date: date | None = None,
):
    table_path = self.top_n_ads_per_shop_and_month_by_spend_path
    performance_df = read_csv_from_s3(self.url_performance_df)
    # neither url is used by more than one shop
    assert (performance_df.groupby("url").apply(lambda df: df.shop_id.nunique()) > 1).sum() == 0
    if start_date is not None:
        performance_df["year_month_date"] = performance_df.year_month.apply(
            lambda x: datetime.strptime(x, "%Y-%m")
        )
        performance_df = performance_df[
            (performance_df.year_month_date >= start_date) & (performance_df.year_month_date <= end_date)
        ]
        performance_df.drop(columns=["year_month_date"], inplace=True)

    top_ads = (
        performance_df.groupby(["shop_id", "year_month"])
        .apply(lambda df: df.sort_values("spend").tail(n_ads_per_shop))
        .reset_index(drop=True)
    )

    save_csv_to_s3(top_ads, path=table_path, index=False)
