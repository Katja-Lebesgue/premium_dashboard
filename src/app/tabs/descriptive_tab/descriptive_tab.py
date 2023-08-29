import os
from abc import abstractproperty
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Literal

from src.abc.descriptive import Descriptive, DescriptiveDF
from src.app.frontend_names import get_frontend_name
from src.utils import *

metrics = [cr, ctr, cpm]


class DescriptiveTab(Descriptive):
    @abstractproperty
    def available_metrics(self) -> list[str]:
        ...

    @abstractproperty
    def show(self, **kwargs) -> None:
        ...

    last_n_months = 3
    colors = ["gold", "mediumturquoise", "darkorange", "lightgreen"]

    def pie_charts(
        self,
        summary_df: pd.DataFrame,
        add_title: bool = True,
        func: Literal["mean", "sum"] = "sum",
    ) -> None:
        last_n_months_series = (
            summary_df.year_month.drop_duplicates().nlargest(n=self.last_n_months).sort_values()
        )
        summary_df = summary_df[summary_df.year_month.isin(last_n_months_series.tolist())]

        col1, col2 = st.columns([1, 4])

        with col1:
            selected_metric = st.radio(
                "Select metric",
                options=self.available_metrics,
                format_func=get_frontend_name,
            )

            last_n_months_series = last_n_months_series.apply(lambda x: datetime.strftime(x, "%b %Y"))
            last_three_months_df = pd.DataFrame(last_n_months_series).rename(
                columns={"year_month": "Period for pie charts"}
            )
            st.dataframe(last_three_months_df.style, hide_index=True)

        with col2:
            fig = make_subplots(
                rows=1,
                cols=len(self.pie_columns),
                specs=[[{"type": "domain"}] * len(self.pie_columns)],
                horizontal_spacing=0.1,
                vertical_spacing=0.1,
            )

            for idx, descriptive_column in enumerate(self.pie_columns):
                add_pie_subplot(
                    fig=fig,
                    df=summary_df,
                    descriptive_column=descriptive_column,
                    metric=selected_metric,
                    plot_row_idx=1,
                    plot_column_idx=idx + 1,
                    func=func,
                )

            # Creating title
            if add_title:
                feature_series = summary_df.loc[summary_df.feature == self.fake_feature, selected_metric]
                if selected_metric.startswith("n_"):
                    total_number = feature_series.mean()
                else:
                    total_number = feature_series.sum()
                total_str = big_number_human_format(total_number)

                if "USD" in selected_metric:
                    currency = "$"
                else:
                    currency = ""

                if selected_metric.startswith("n_"):
                    unit = selected_metric.removeprefix("n_")
                else:
                    unit = get_frontend_name(selected_metric)

                title_text = f"Total: {currency}{total_str} {unit}"

                title = {
                    "x": 0.5,
                    "text": title_text,
                    "font": {"size": 25},
                }
            else:
                title = {}

            fig.update_traces(
                textposition="inside",
                textinfo="percent+label",
                # marker={"colors": self.colors},
                textfont_size=15,
            )
            fig.update_layout(height=500, width=900, showlegend=False, title=title)
            st.plotly_chart(fig)

    def descriptive_features_through_time(
        self, summary_df: pd.DataFrame, show_relative_option: bool = True
    ) -> None:
        col1, col2 = st.columns([1, 3])
        with col1:
            selected_feature = st.selectbox(
                "Select feature",
                options=self.descriptive_columns,
                format_func=get_frontend_name,
            )

            selected_metric = st.selectbox(
                "Select metric",
                options=self.metric_columns,
                format_func=get_frontend_name,
            )

            feature_df = summary_df[summary_df.feature == selected_feature]
            metric_by_month_and_value = feature_df.groupby(["year_month", "feature_value"])[
                selected_metric
            ].sum()

            if show_relative_option:
                bar_height = st.select_slider("Adjust bar height", ("Absolute", "Relative"), value="Relative")

                if bar_height == "Relative":
                    metric_by_month = feature_df.groupby("year_month")[selected_metric].sum()
                    metric_by_month_and_value = metric_by_month_and_value / metric_by_month

            metric_by_month_and_value_df = pd.DataFrame(metric_by_month_and_value).reset_index()

        extra_bar_kwargs = {}
        if "color" in selected_feature:
            extra_bar_kwargs["color_discrete_map"] = {c: c for c in feature_df.feature_value.unique()}

        with col2:
            fig = px.bar(
                metric_by_month_and_value_df,
                x="year_month",
                y=selected_metric,
                color="feature_value",
                title="Features through time",
                **extra_bar_kwargs,
            )

            fig.update_layout(
                barmode="stack",
                xaxis_title=get_frontend_name("month"),
                yaxis_title=get_frontend_name(selected_metric),
                legend_title="value",
            )

            st.plotly_chart(fig)

    def benchmarks(self, main_df: pd.DataFrame) -> None:
        col1, col2 = st.columns([1, 3])
        with col1:
            selected_feature = st.selectbox(
                "Select feature",
                options=self.descriptive_columns,
                format_func=get_frontend_name,
                key="time_feature",
            )
            selected_metric = st.selectbox(
                "Select metric",
                options=metrics,
                format_func=lambda x: get_frontend_name(str(x)),
                key="time_metric",
            )

        feature_df = main_df[main_df.feature == selected_feature]
        feature_df = feature_df[
            feature_df[selected_metric.denom] > max(100, feature_df[selected_metric.denom].quantile(0.25))
        ]

        with col2:
            fig = go.Figure()
            feature_values = feature_df.feature_value.unique().tolist()
            for value in feature_values:
                extra_box_kwargs = {}
                if "color" in selected_feature:
                    extra_box_kwargs = extra_box_kwargs | {"fillcolor": value, "line": {"color": value}}
                fig.add_trace(
                    go.Box(
                        y=feature_df.loc[feature_df.feature_value == value, str(selected_metric)],
                        name=get_frontend_name(value),
                        boxmean=True,
                        boxpoints=False,
                        **extra_box_kwargs,
                    )
                )

                fig.add_annotation(
                    x=get_frontend_name(value),
                    y=feature_df[feature_df["feature_value"] == value][str(selected_metric)].max(),
                    text=f"n = {big_number_human_format(len(feature_df[feature_df.feature_value == value]))}",
                    yshift=20,
                    showarrow=False,
                )
                fig.add_annotation(
                    x=get_frontend_name(value),
                    y=feature_df[feature_df["feature_value"] == value][str(selected_metric)].median(),
                    text=f"md = {big_number_human_format(feature_df.loc[feature_df.feature_value == value, str(selected_metric)].median(), small_decimals=1)}",
                    yshift=8,
                    showarrow=False,
                )
            fig.update_layout(
                title={"text": "Benchmarks"},
                yaxis_title=f"{selected_metric} ({selected_metric.unit})",
            )

            st.plotly_chart(fig)


def add_pie_subplot(
    fig,
    df: pd.DataFrame,
    descriptive_column: str,
    metric: str,
    plot_row_idx: int,
    plot_column_idx: int,
    func: Literal["sum", "mean"],
):
    pie_df = df[df.feature == descriptive_column]
    pie_df = pd.DataFrame(getattr(pie_df.groupby("feature_value")[metric], func)()).reset_index()

    if descriptive_column.startswith("n_"):
        func = "mean"

    fig.add_trace(
        go.Pie(
            values=pie_df[metric],
            labels=pie_df["feature_value"],
            hoverinfo="label+value+percent",
            title=dict(
                text=get_frontend_name(descriptive_column),
                font=dict(size=25),
                position="top left",
            ),
            rotation=225,
        ),
        row=plot_row_idx,
        col=plot_column_idx,
    )

    if "color" in descriptive_column:
        fig.update_traces(marker={"colors": pie_df.feature_value.tolist()})
