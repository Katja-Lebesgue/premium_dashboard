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

PERF_COLUMNS = ["spend", "impressions", "link_clicks", "purchases", "ctr"]


def image_analysis():
    color_df_s3_path = s3_image.final_df
    color_df = st_read_csv_from_s3(color_df_s3_path, add_global_path=True)

    color_df["year_month"] = color_df.year_month.apply(lambda x: datetime.strptime(x, "%Y-%m"))
    color_df["ctr"] = color_df.link_clicks.div(color_df.impr)

    col, _ = st.columns([1, 2])
    with col:
        total_or_shop_average = st.selectbox(label="Choose wisely:", options=["Total", "Shop average"])

    if total_or_shop_average == "Shop average":
        color_df = color_df.drop(columns=s3_image.performance_columns)
        color_df = color_df.rename(columns={col: col.removeprefix("relative_") for col in color_df})

    pie_charts(
        color_df=color_df.copy(),
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
            PERF_COLUMNS,
            format_func=lambda x: x.replace("_", " "),
            key="descriptive_metric",
        )

        # timetable creation
        last_3_months_str = last_3_months.apply(lambda x: datetime.strftime(x, "%b %Y"))

        st.markdown(hide_table_row_index(), unsafe_allow_html=True)

        time_df = pd.DataFrame(last_3_months_str).rename(columns=dict(year_month="Time period"))
        st.table(time_df)

    with col2:
        fig = px.pie(
            color_df,
            values=descriptive_metric,
            names="color",
            color="color",
            color_discrete_map={c: c for c in color_df.color.unique()},
        )

        fig.update_layout(
            title={"text": "12 predominant colors on facebook ads in last three months", "x": 0.5}
        )

        st.plotly_chart(fig)


def text_features_through_time(color_df: pd.DataFrame) -> None:
    col1, col2 = st.columns([1, 3])

    with col1:
        performance_metric = st.selectbox(
            "Select metric",
            PERF_COLUMNS,
            format_func=lambda x: x.replace("_", " "),
            key="performance_metric",
        )

        bar_height = st.select_slider("Adjust bar height", ("Absolute", "Relative"), value="Relative")

        performance_series = color_df.groupby(["year_month", "color"])[performance_metric].sum()
        performance_series.name = performance_metric

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
            title="Colors over time",
            color_discrete_map={c: c for c in color_df.color.unique()},
        )

        fig.update_layout(
            barmode="stack",
        )

        st.plotly_chart(fig)
