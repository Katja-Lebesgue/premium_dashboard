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


analysis_type_help = (
    "Select which kind of analysis you want to see. This select box changes the content"
    " of the whole page (including time graph). If you select _total_, you will see sum"
    " of all metrics in the selected period, i.e. total spend of all Lebesgue shops in"
    " June 2023, and if you select _by shop_, the number displayed will"
    " correspond to the average metric by shop, i.e. how much an average shop spent in"
    " June 2023."
)


class DescriptiveTab(Descriptive):
    def __init__(self):
        self.available_metrics = self.metric_columns + ["n_shops"]

    last_n_months = 3
    colors = ["gold", "mediumturquoise", "darkorange", "lightgreen"]

    @abstractproperty
    def pie_columns(self) -> list[str]:
        ...

    def show(self) -> None:
        st.markdown(hide_table_row_index(), unsafe_allow_html=True)
        main_df = self.get_most_recent_summary_df(tag=self.tag, convert_str_to_date=True)

        col1, _ = st.columns([1, 2])
        with col1:
            analysis_type = st.selectbox(
                label="Analysis type",
                options=("total", "by shop"),
                help=analysis_type_help,
            )

        if analysis_type == "by shop":
            main_df = main_df.drop(columns=self.metric_columns)
            main_df = main_df.rename(columns={col + "_by_shop": col for col in self.metric_columns})
            pie_func = "mean"
        else:
            pie_func = "sum"

        self.pie_charts(main_df=main_df.copy(), add_title=(analysis_type == "total"), func=pie_func)

        self.descriptive_features_through_time(main_df=main_df)

    @st.cache_data
    def get_most_recent_summary_df(_self, tag: str, convert_str_to_date: bool = True):
        end_date = max(_self.get_available_dates(df_type=DescriptiveDF.summary))
        main_df = _self.read_df(df_type=DescriptiveDF.summary, end_date=end_date)
        if convert_str_to_date:
            main_df["year_month"] = main_df.year_month.apply(lambda x: datetime.strptime(x, "%Y-%m"))
        return main_df

    def pie_charts(
        self, main_df: pd.DataFrame, add_title: bool = True, func: Literal["mean", "sum"] = "sum"
    ) -> None:
        last_n_months_series = (
            main_df.year_month.drop_duplicates().nlargest(n=self.last_n_months).sort_values()
        )
        main_df = main_df[main_df.year_month.isin(last_n_months_series.tolist())]

        col1, col2 = st.columns([1, 4])

        with col1:
            selected_metric = st.radio(
                "Select metric",
                options=self.available_metrics,
                format_func=get_frontend_name,
            )

            last_n_months_series = last_n_months_series.apply(lambda x: datetime.strftime(x, "%b %Y"))
            last_three_months_df = pd.DataFrame(last_n_months_series).rename(
                columns={"year_month": "Observed time period"}
            )
            st.table(last_three_months_df.style.hide(axis="index"))

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
                    df=main_df,
                    descriptive_column=descriptive_column,
                    metric=selected_metric,
                    plot_row_idx=1,
                    plot_column_idx=idx + 1,
                    func=func,
                )

            # Creating title
            if add_title:
                total_df = main_df.loc[main_df.feature == self.fake_feature, selected_metric]

                if selected_metric.startswith("n_"):
                    total_number = total_df.mean()
                else:
                    total_number = total_df.sum()
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
                marker={"colors": self.colors},
                textfont_size=15,
            )
            fig.update_layout(height=500, width=900, showlegend=False, title=title)
            st.plotly_chart(fig)

    def descriptive_features_through_time(self, main_df: pd.DataFrame) -> None:
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

            main_df = main_df[main_df.feature == selected_feature]
            metric_by_month_and_value = main_df.groupby(["year_month", "feature_value"])[
                selected_metric
            ].sum()

            bar_height = st.select_slider("Adjust bar height", ("Absolute", "Relative"), value="Relative")

            if bar_height == "Relative":
                metric_by_month = main_df.groupby("year_month")[selected_metric].sum()
                metric_by_month_and_value = metric_by_month_and_value / metric_by_month

            metric_by_month_and_value_df = pd.DataFrame(metric_by_month_and_value).reset_index()

        with col2:
            fig = px.bar(
                metric_by_month_and_value_df,
                x="year_month",
                y=selected_metric,
                color="feature_value",
                title="Performance",
            )

            fig.update_layout(
                barmode="stack",
                xaxis_title=get_frontend_name("month"),
                yaxis_title=get_frontend_name(selected_metric),
                legend_title="value",
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
