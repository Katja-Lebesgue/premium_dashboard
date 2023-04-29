import sys

sys.path.append("./.")

import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from loguru import logger
from plotly.subplots import make_subplots

from src.app.utils.cache_functions import st_read_csv_from_s3
from src.app.utils.css import hide_table_row_index
from src.app.utils.labels_and_values import *
from src.app.utils.labels_and_values import feature_dict_market
from src.s3 import *
from src.utils import big_number_human_format

load_dotenv()

PERF_COLUMNS = ["spend", "impressions", "link_clicks", "purchases"]


def image_analysis():
    color_df_s3_path = s3_image.final_df
    color_df = st_read_csv_from_s3(color_df_s3_path, add_global_path=True)

    color_df["year_month"] = color_df.year_month.apply(lambda x: datetime.strptime(x, "%Y-%m"))

    col, _ = st.columns([1, 2])
    with col:
        total_or_shop_average = st.selectbox(label="Choose wisely:", options=["Total", "Shop average"])

    st.write(color_df.columns)
    if total_or_shop_average == "Shop average":
        for perf_col in s3_image.performance_columns:
            group_idx = ["shop_id", "year_month"]
            full_idx = group_idx + ["ad_id"]

            sum_by_shop_and_month = color_df.groupby(group_idx)[perf_col].sum()

            color_df_with_full_index = color_df.set_index(full_idx)
            relative_spend = pd.Series(
                color_df_with_full_index.spend.div(sum_by_shop_and_month), name=f"relative_{perf_col}"
            )
            color_df = color_df_with_full_index.join(relative_spend).reset_index()
            color_df.drop(columns=[perf_col], inplace=True)
            color_df.rename(columns={f"relative_{perf_col}": perf_col}, inplace=True)

    pie_charts(
        color_df.copy(),
        add_title=(total_or_shop_average == "Total"),
    )

    text_features_through_time(color_df.copy())

    pass


def pie_charts(color_df: pd.DataFrame, add_title: bool = True) -> None:
    last_3_months = (
        color_df.year_month.drop_duplicates()
        .sort_values(ascending=False)
        .reset_index(drop=True)
        .head(3)
        .sort_values(ascending=True)
    )

    color_df = color_df.loc[color_df.year_month.isin(last_3_months), :]

    col1, col2 = st.columns([1, 4])

    with col1:
        descriptive_metric = st.radio(
            "Select metric",
            s3_image.performance_columns,
            format_func=lambda x: x.replace("_", " "),
            key="descriptive_metric",
        )

        # timetable creation
        last_3_months_str = last_3_months.apply(lambda x: datetime.strftime(x, "%b %Y"))

        st.markdown(hide_table_row_index(), unsafe_allow_html=True)

        time_df = pd.DataFrame(last_3_months_str).rename(columns=dict(year_month="Time period"))
        st.table(time_df)

    with col2:
        color_columns = [column for column in color_df.columns if column[0] == "#"]
        pie_data = pd.Series(
            color_df[color_columns].apply(lambda s: s.multiply(color_df[descriptive_metric])).sum(),
            name=descriptive_metric,
        ).rename_axis("color")
        pie_data = pd.DataFrame(pie_data).reset_index()

        fig = px.pie(
            pie_data,
            values=descriptive_metric,
            names="color",
            color="color",
            color_discrete_map={c: c for c in color_columns},
        )

        st.plotly_chart(fig)


def text_features_through_time(color_df: pd.DataFrame) -> None:
    col1, col2 = st.columns([1, 3])

    with col1:
        performance_metric = st.selectbox(
            "Select metric",
            ("spend",),
            format_func=lambda x: x.replace("_", " "),
            key="performance_metric",
        )

        color_columns = [col for col in color_df.columns if col[0] == "#"]
        color_df[color_columns] = color_df[color_columns].apply(
            lambda s: s.multiply(color_df[performance_metric]), axis=0
        )
        color_df.drop(columns=[performance_metric], inplace=True)
        noncolor_columns = [col for col in color_df.columns if col[0] != "#"]
        color_df = (
            color_df.set_index(noncolor_columns)
            .stack(level=0)
            .reset_index()
            # .rename(columns={"level_5": "color", 0: performance_metric})
        )

        bar_height = st.select_slider("Adjust bar height", ("Absolute", "Relative"), value="Relative")

        performance_series = color_df.groupby(["year_month", "color"])[performance_metric].sum()

        if bar_height == "Relative":
            monthly = color_df.groupby("year_month")[performance_metric].sum()
            performance_series = performance_series / monthly

        bar_data = pd.DataFrame(performance_series).reset_index()

    with col2:
        fig = px.bar(
            bar_data,
            x="year_month",
            y=performance_metric,
            color="color",
            title="Performance",
            color_discrete_map={c: c for c in color_columns},
        )

        fig.update_layout(barmode="stack")

        st.plotly_chart(fig)
