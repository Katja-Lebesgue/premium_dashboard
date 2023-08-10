from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from metadata.globals import *
from src.app.utils.css import hide_table_row_index
from src.app.utils.labels_and_values import *
from src.app.utils.labels_and_values import feature_dict
from src.utils import big_number_human_format


def descriptive_statistics(data_shop: pd.DataFrame):
    if not len(data_shop):
        st.warning("No data")
        return

    pie_charts(data_shop.copy())

    text_features_through_time(data_shop)


def pie_charts(data_shop: pd.DataFrame) -> None:
    last_3_months = (
        data_shop.year_month.drop_duplicates()
        .sort_values(ascending=False)
        .reset_index(drop=True)
        .head(3)
        .sort_values(ascending=True)
    )

    data_shop = data_shop.loc[data_shop.year_month.isin(last_3_months), :]

    col1, col2 = st.columns([1, 4])

    with col1:
        # metric selection
        descriptive_metric = st.radio(
            "Select metric",
            tuple(metric_dict_shop.keys()),
            format_func=lambda x: metric_dict_shop[x],
            key="descriptive_metric",
        )

        # targeting selection
        targeting = st.radio(
            "Select targets",
            tuple(targeting_dict.keys()),
            format_func=lambda x: targeting_dict[x],
            key="pie_targeting",
            index=2,
        )

        if targeting in ["targets_US", "targets_english"]:
            data_shop = data_shop.loc[data_shop[targeting] == True, :]

        # timetable creation
        last_3_months_str = last_3_months.apply(lambda x: datetime.strftime(x, "%b %Y"))

        st.markdown(hide_table_row_index(), unsafe_allow_html=True)

        time_df = pd.DataFrame(last_3_months_str).rename(columns=dict(year_month="Time period"))
        st.table(time_df)

        if descriptive_metric == "count":
            data_shop = data_shop.drop_duplicates(subset="ad_id")

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
            df=data_shop,
            group="creative_type",
            y=descriptive_metric,
            row=1,
            col=1,
        )
        add_pie_subplot(
            fig=fig,
            df=data_shop,
            group="discounts_any",
            y=descriptive_metric,
            row=1,
            col=2,
        )
        add_pie_subplot(fig=fig, df=data_shop, group="target", y=descriptive_metric, row=1, col=3)

        # Creating title
        total_str = big_number_human_format(data_shop[descriptive_metric].sum())

        if descriptive_metric == "spend_USD":
            currency = "$"
        else:
            currency = ""

        if descriptive_metric == "counts":
            unit = "ads"
        else:
            unit = metric_dict_shop[descriptive_metric]

        fig.update_traces(textinfo="percent+label", marker=dict(colors=colors), textfont_size=15)
        fig.update_layout(
            height=500,
            width=900,
            showlegend=False,
            title=dict(
                x=0.5,
                text=f"Total: {currency}{total_str} {unit}",
                font=dict(size=25),
            ),
        )

        st.plotly_chart(fig)


def add_pie_subplot(fig, df: pd.DataFrame, group: str, y: str, row: int, col: int):
    pie_df = pd.DataFrame(df.replace({None: "unknown"}).groupby(group).sum()[y]).reset_index()

    fig.add_trace(
        go.Pie(
            values=pie_df[y],
            labels=pie_df[group],
            hoverinfo="label+value+percent",
            title=dict(text=pie_groups_dict[group], font=dict(size=25), position="top left"),
            rotation=225,
        ),
        row=row,
        col=col,
    )

    return


def text_features_through_time(data_shop: pd.DataFrame) -> None:
    col1, col2 = st.columns([1, 3])

    with col1:
        text_feature = st.selectbox(
            "Select feature",
            tuple(feature_dict.keys()),
            format_func=lambda x: feature_dict[x],
        )

        performance_metric = st.selectbox(
            "Select metric",
            tuple(metric_dict_shop.keys()),
            format_func=lambda x: metric_dict_shop[x],
            key="performance_metric",
        )

        targeting = st.radio(
            "Select targets",
            tuple(targeting_dict.keys()),
            format_func=lambda x: targeting_dict[x],
            key="time_targeting",
            index=2,
        )

        if targeting in ["targets_US", "targets_english"]:
            data_shop = data_shop.loc[data_shop[targeting] == True, :]

        if performance_metric == "counts":
            data_shop = data_shop.drop_duplicates(subset="ad_id")

        performance_series = data_shop.groupby(["year_month", text_feature]).sum()[performance_metric]

        bar_height = st.select_slider("Adjust bar height", ("Absolute", "Relative"), value="Relative")

        if bar_height == "Relative":
            monthly = data_shop.groupby("year_month").sum()[performance_metric]
            performance_series = performance_series / monthly

        performance_data = pd.DataFrame(performance_series).reset_index()

    with col2:
        fig = px.bar(
            performance_data,
            x="year_month",
            y=performance_metric,
            color=text_feature,
            title="Performance",
        )

        fig.update_layout(barmode="stack")

        st.plotly_chart(fig)
