from datetime import date, datetime

import pandas as pd

from src.database.session import SessionLocal
from src.image_analysis.utils import *
from src.models import *
from src.utils import *

db = SessionLocal()

# TODO: global perf columns
PERFORMANCE_COLUMNS = ["spend_USD", "link_clicks", "purch", "impr", "purch_value"]


def save_final(
    self,
):
    perf_df = read_csv_from_s3(self.url_performance_df)
    image_df = read_csv_from_s3(self.image_df)

    image_df = image_df[image_df.global_color_centroids.notna()]
    image_df.global_color_centroids = image_df.global_color_centroids.apply(
        lambda x: {rgb_to_hex(k): v for k, v in x.items()}
    )
    unpacked_colors = image_df.global_color_centroids.apply(pd.Series).fillna(0)
    scaled_colors = unpacked_colors.div(unpacked_colors.sum(axis=1), axis=0)
    image_df = image_df.join(scaled_colors)

    full_df = perf_df.merge(image_df, on="url")
    full_df = full_df[full_df.shop_id != 37673090]
    final_df_by_shop = pd.DataFrame()
    color_cols = [col for col in full_df.columns if col[0] == "#"]
    assert all([perf_col in full_df.columns for perf_col in self.performance_columns])
    for perf_col in self.performance_columns:
        relative_perf_col = f"relative_{perf_col}"
        color_df = full_df.copy()
        group_idx = ["shop_id", "year_month"]
        full_idx = group_idx + ["ad_id"]

        sum_by_shop_and_month = color_df.groupby(group_idx)[perf_col].sum()

        color_df_with_full_index = color_df.set_index(full_idx)
        relative_perf_series = pd.Series(
            color_df_with_full_index[perf_col].div(sum_by_shop_and_month), name=relative_perf_col
        )

        color_df = color_df_with_full_index.join(relative_perf_series).reset_index()
        if (color_df.groupby(["shop_id", "year_month"])[relative_perf_col].sum() - 1 > 1e-2).sum() != 0:
            logger.debug("fail")

        color_df = color_df.loc[
            :, color_cols + ["ad_id", "year_month", "shop_id", perf_col, relative_perf_col]
        ]

        noncolor_columns = [col for col in color_df.columns if col[0] != "#"]
        color_df = (
            color_df.set_index(noncolor_columns)
            .stack(level=0)
            .reset_index()
            .rename(columns={"level_5": "color", 0: "freq"})
        )
        for col in [perf_col, relative_perf_col]:
            color_df[col] = color_df.apply(lambda df: df[col] * df["freq"], axis=1)
        color_df = color_df.groupby(["shop_id", "year_month", "color"])[[perf_col, relative_perf_col]].sum()
        final_df_by_shop = pd.concat([final_df_by_shop, color_df], axis=1)

    save_csv_to_s3(final_df_by_shop, path=self.final_by_shop_df, index=True)
    final_df = final_df_by_shop.reset_index().groupby(["color", "year_month"]).sum().drop(columns=["shop_id"])
    save_csv_to_s3(final_df, path=self.final_df, index=True)
