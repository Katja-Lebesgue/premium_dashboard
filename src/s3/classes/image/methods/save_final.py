from datetime import date, datetime

import pandas as pd

from src.database.session import SessionLocal
from src.image_analysis.utils import *
from src.models import *
from src.utils import *

db = SessionLocal()


def save_final(
    self,
):
    table_path = self.final_df
    perf_df = read_csv_from_s3(self.url_performance_df)
    image_df = read_csv_from_s3(self.image_df)
    image_df = image_df[image_df.global_color_centroids.notna()]
    image_df.global_color_centroids = image_df.global_color_centroids.apply(
        lambda x: {rgb_to_hex(k): v for k, v in x.items()}
    )
    unpacked_colors = image_df.global_color_centroids.apply(pd.Series).fillna(0)
    scaled_colors = unpacked_colors.div(unpacked_colors.sum(axis=1), axis=0)
    image_df = image_df.join(scaled_colors)

    final_df = perf_df.merge(image_df, on="url")

    # color_cols = [col for col in final_df.columns if col[0] == "#"]
    # perf_cols = ["spend", "purchases", "impressions", "link_clicks"]
    # color_cols_mean = {col: "mean" for col in color_cols}
    # perf_cols_sum = {col: "sum" for col in perf_cols}
    # grouped_df = (
    #     final_df.groupby(["shop_id", "year_month"]).agg(color_cols_mean | perf_cols_sum).reset_index()
    # )

    save_csv_to_s3(final_df, path=table_path, index=False)
