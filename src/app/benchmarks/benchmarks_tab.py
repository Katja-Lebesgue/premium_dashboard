import os
from abc import abstractproperty
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Literal

from src.abc.descriptive import Descriptive, DescriptiveDF
from src.app.frontend_names import get_frontend_name
from src.app.utils.css import hide_table_row_index
from src.utils import *


metrics = [cr, ctr, cpm]


class BenchmarksTab(Descriptive):
    def __init__(self):
        self.available_metrics = self.metric_columns + ["n_shops"]

    last_n_months = 3
    colors = ["gold", "mediumturquoise", "darkorange", "lightgreen"]

    def show(self) -> None:
        main_df = self.get_most_recent_main_df(tag=self.tag)

        col1, col2 = st.columns([1, 3])
        with col1:
            selected_feature = st.selectbox(
                "Select feature",
                options=self.descriptive_columns,
                format_func=get_frontend_name,
            )
            selected_metric = st.selectbox(
                "Select metric",
                options=metrics,
                format_func=lambda x: get_frontend_name(str(x)),
            )

        feature_df = main_df[main_df.feature == selected_feature]

        with col2:
            fig = go.Figure()
            feature_values = feature_df.feature_value.unique().tolist()
            for value in feature_values:
                fig.add_trace(
                    go.Box(
                        y=feature_df.loc[feature_df.feature_value == value, str(selected_metric)],
                        name=get_frontend_name(value),
                        boxmean=True,
                        boxpoints=False,
                    )
                )
            fig.update_layout(
                title={"text": "Metric boxplot by feature"},
                yaxis_title=f"{selected_metric} ({selected_metric.unit})",
                xaxis_title=get_frontend_name(selected_feature),
            )

            st.plotly_chart(fig)

    @st.cache_data
    def get_most_recent_main_df(_self, tag: str, convert_str_to_date: bool = True):
        end_date = max(_self.get_available_dates(df_type=DescriptiveDF.main))
        main_df = _self.read_df(df_type=DescriptiveDF.main, end_date=end_date)
        if convert_str_to_date:
            main_df["year_month"] = main_df.year_month.apply(lambda x: datetime.strptime(x, "%Y-%m"))
        for metric in metrics:
            main_df[str(metric)] = main_df.apply(metric.formula_series, axis=1)
        return main_df[main_df.spend_USD > max(100, main_df.spend_USD.quantile(0.25))]
