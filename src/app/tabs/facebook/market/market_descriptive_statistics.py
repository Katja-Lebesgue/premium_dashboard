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

from src.app.utils.css import hide_table_row_index
from src.app.utils.labels_and_values import *
from src.app.utils.labels_and_values import feature_dict_market
from src.s3 import *
from src.utils import *

load_dotenv()


def market_descriptive_statistics(
    s3_path: str = f"data/global/global_descriptive",
):
    list_of_objects = pd.Series(list_objects_from_prefix(prefix=s3_path)).sort_values()

    descriptive_df_path = list_of_objects[len(list_of_objects) - 2]

    descriptive_df = read_csv_from_s3(descriptive_df_path, add_global_folder=False)

    descriptive_df["year_month"] = descriptive_df.year_month.apply(lambda x: datetime.strptime(x, "%Y-%m"))

    col, _ = st.columns([1, 2])
    with col:
        total_or_shop_average = st.selectbox(label="Choose wisely:", options=["Total", "Shop average"])

    if total_or_shop_average == "Shop average":
        proper_metric_dict = metric_dict | {"count_ads": "ads"}
        descriptive_df.drop(list(proper_metric_dict.keys()), axis=1, inplace=True)
        descriptive_df.columns = [col.replace("_by_shop", "") for col in descriptive_df.columns]
        proper_metric_dict = proper_metric_dict | {"count_ads": "ads"}
    else:
        proper_metric_dict = metric_dict_market

    pie_charts(
        descriptive_df.copy(),
        proper_metric_dict=proper_metric_dict,
        add_title=(total_or_shop_average == "Total"),
    )

    text_features_through_time(descriptive_df)


def pie_charts(descriptive_df: pd.DataFrame, proper_metric_dict: dict, add_title: bool = True) -> None:
    last_3_months = (
        descriptive_df.year_month.drop_duplicates()
        .sort_values(ascending=False)
        .reset_index(drop=True)
        .head(3)
        .sort_values(ascending=True)
    )

    descriptive_df = descriptive_df.loc[descriptive_df.year_month.isin(last_3_months), :]

    col1, col2 = st.columns([1, 4])

    with col1:
        # metric selection
        descriptive_metric = st.radio(
            "Select metric",
            tuple(proper_metric_dict.keys()),
            format_func=lambda x: proper_metric_dict[x],
            key="descriptive_metric",
        )

        # timetable creation
        last_3_months_str = last_3_months.apply(lambda x: datetime.strftime(x, "%b %Y"))

        st.markdown(hide_table_row_index(), unsafe_allow_html=True)

        time_df = pd.DataFrame(last_3_months_str).rename(columns=dict(year_month="Time period"))
        st.table(time_df)

    with col2:
        fig = make_subplots(
            rows=1,
            cols=3,
            specs=[[{"type": "domain"}, {"type": "domain"}, {"type": "domain"}]],
            horizontal_spacing=0.1,
            vertical_spacing=0.1,
        )

        colors = ["gold", "mediumturquoise", "darkorange", "lightgreen"]

        fig.update_traces(textposition="inside", textinfo="percent+label", marker=dict(colors=colors))

        add_pie_subplot(
            fig=fig,
            df=descriptive_df,
            group="creative_type",
            y=descriptive_metric,
            row=1,
            col=1,
        )
        add_pie_subplot(
            fig=fig,
            df=descriptive_df,
            group="discounts_any",
            y=descriptive_metric,
            row=1,
            col=2,
        )
        add_pie_subplot(
            fig=fig,
            df=descriptive_df,
            group="target",
            y=descriptive_metric,
            row=1,
            col=3,
        )

        # Creating title
        if add_title:
            total_str = big_number_human_format(
                descriptive_df.loc[descriptive_df.feature == "target", descriptive_metric].sum()
            )

            if descriptive_metric == "spend_USD":
                currency = "$"
            else:
                currency = ""

            if descriptive_metric == "counts":
                unit = "ads"
            else:
                unit = metric_dict_market[descriptive_metric]

            title = dict(
                x=0.5,
                text=f"Total: {total_str}{currency} {unit}",
                font=dict(size=25),
            )
        else:
            title = None

        fig.update_traces(textinfo="percent+label", marker=dict(colors=colors), textfont_size=15)
        fig.update_layout(height=500, width=900, showlegend=False, title=title)

        st.plotly_chart(fig)


def add_pie_subplot(fig, df: pd.DataFrame, group: str, y: str, row: int, col: int):
    pie_df = df[df.feature == group]

    pie_df = pd.DataFrame(pie_df.groupby("feature_value").sum()[y]).reset_index()

    fig.add_trace(
        go.Pie(
            values=pie_df[y],
            labels=pie_df["feature_value"],
            hoverinfo="label+value+percent",
            title=dict(text=pie_groups_dict[group], font=dict(size=25), position="top left"),
            rotation=225,
        ),
        row=row,
        col=col,
    )

    return


def text_features_through_time(descriptive_df: pd.DataFrame) -> None:
    col1, col2 = st.columns([1, 3])

    features = descriptive_df.feature.unique()

    metrics = set(descriptive_df.columns) - {"feature", "feature_value", "year_month"}

    with col1:
        selected_feature = st.selectbox(
            "Select feature", tuple(features), format_func=lambda x: x.removesuffix("_any")
        )

        performance_metric = st.selectbox(
            "Select metric",
            tuple(metric_dict_market.keys()),
            format_func=lambda x: metric_dict_market[x],
            key="performance_metric",
        )

        descriptive_df = descriptive_df[descriptive_df.feature == selected_feature]
        performance_series = descriptive_df.groupby(["year_month", "feature_value"]).sum()[performance_metric]

        bar_height = st.select_slider("Adjust bar height", ("Absolute", "Relative"), value="Relative")

        if bar_height == "Relative":
            monthly = descriptive_df.groupby("year_month").sum()[performance_metric]
            performance_series = performance_series / monthly

        performance_data = pd.DataFrame(performance_series).reset_index()

    with col2:
        fig = px.bar(
            performance_data,
            x="year_month",
            y=performance_metric,
            color="feature_value",
            title="Performance",
        )

        fig.update_layout(barmode="stack")

        st.plotly_chart(fig)
