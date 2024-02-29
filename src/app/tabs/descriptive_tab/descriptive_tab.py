from abc import abstractmethod
from typing import Literal
import itertools

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
from scipy.stats import kruskal

from src.interfaces.descriptive import Descriptive
from src.app.frontend_names import get_frontend_name, list_to_str
from src.statistical_tests import perform_test_on_df
from src.app.utils import filter_df, FilterType
from src.utils import *


class DescriptiveTab(Descriptive):
    def available_metrics(self) -> list[str]:
        return []

    @abstractmethod
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
        st.subheader("Recent trends")
        last_n_months_series = (
            summary_df.year_month.drop_duplicates().nlargest(n=self.last_n_months).sort_values()
        )
        summary_df = summary_df[summary_df.year_month.isin(last_n_months_series.tolist())]

        col1, col2 = st.columns([1, 4])

        with col1:
            selected_metric = st.radio(
                "Select metric",
                options=self.metric_columns,
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
        st.subheader("Features through time")
        col1, col2 = st.columns([1, 3])
        with col1:
            selected_feature = st.selectbox(
                "Select feature",
                options=[
                    feature
                    for feature in self.descriptive_columns
                    if feature in set(summary_df.feature.unique())
                ],
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
                relative_bar_height = st.toggle(label="Relative bar height", value=True)

                if relative_bar_height is True:
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
        st.subheader("Tests")
        col1, col2 = st.columns([1, 3])

        with col1:
            main_df = filter_df(
                df=main_df,
                column_name="year_month",
                filter_type=FilterType.select_slider,
                format_func=lambda date_time: date_time.strftime("%Y-%m"),
                slider_default_lower_bound=datetime(year=2015, month=1, day=1),
            )

            selected_metric = st.selectbox(
                "Select metric",
                options=self.metrics,
                format_func=lambda x: get_frontend_name(str(x)),
                key="time_metric",
            )

            main_df = main_df[
                main_df[str(selected_metric)].apply(lambda value: value in selected_metric.interval)
            ]

            selected_feature = st.selectbox(
                "Select feature",
                options=[
                    feature
                    for feature in self.descriptive_columns
                    if feature in set(main_df.feature.unique())
                ],
                format_func=get_frontend_name,
                key="time_feature",
            )

            feature_df = main_df[main_df.feature == selected_feature]

            feature_df = feature_df[
                feature_df[selected_metric.denom] > max(100, feature_df[selected_metric.denom].quantile(0.25))
            ]

            partition, _ = perform_test_on_df(
                df=feature_df,
                group_column="feature_value",
                metric_column=str(selected_metric),
                test_func=kruskal,
                test_func_kwargs={"nan_policy": "omit"},
                pd_feature_func="median",
            )

            if (n_groups := len(sum(partition, []))) > 1:
                if (n_slices := len(partition)) == 1:
                    st.warning(
                        f"There is no significant difference in {get_frontend_name(selected_metric)} among the groups."
                    )
                else:
                    winners = partition[0]
                    losers = partition[-1]
                    winners_str = list_to_str(winners)
                    if winners_str.islower():
                        winners_str = winners_str.capitalize()
                    losers_str = list_to_str(losers)
                    winners_verb = "has" if len(winners) == 1 else "have"
                    losers_verb = "has" if len(losers) == 1 else "have"
                    if n_slices == 2:
                        message = f"{winners_str} {winners_verb} significantly higher {selected_metric} than {losers_str}."
                    else:
                        message = f"{winners_str} {winners_verb} significantly the highest {selected_metric}, while {losers_str} {losers_verb} the lowest."
                    st.success(message)

        with col2:
            fig = go.Figure()
            boxplot_idx = 0
            for slice in partition:
                for value in slice:
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

                    # write sample size on boxplot
                    fig.add_annotation(
                        x=get_frontend_name(value),
                        y=feature_df[feature_df["feature_value"] == value][str(selected_metric)].max(),
                        text=f"n = {big_number_human_format(len(feature_df[feature_df.feature_value == value]))}",
                        yshift=20,
                        showarrow=False,
                    )
                    # write median on boxplot
                    fig.add_annotation(
                        x=get_frontend_name(value),
                        y=feature_df[feature_df["feature_value"] == value][str(selected_metric)].median(),
                        text=f"md = {big_number_human_format(feature_df.loc[feature_df.feature_value == value, str(selected_metric)].median(), small_decimals=1)}",
                        yshift=8,
                        showarrow=False,
                    )
                    boxplot_idx += 1

                if boxplot_idx < n_groups:
                    fig.add_vline(x=boxplot_idx - 0.5, line_width=3, line_dash="dash", line_color="green")
            fig.update_layout(
                yaxis_title=f"{selected_metric} ({selected_metric.unit})",
            )

            st.plotly_chart(fig)

        generate_table_button = st.button("Compute significance table")

        if generate_table_button:
            significance_table = pd.DataFrame(columns=["metric", "feature", "higher"])
            for feature, metric in itertools.product(self.descriptive_columns, self.metrics):
                feature_df = main_df[main_df.feature == feature]
                feature_df = feature_df[
                    feature_df[metric.denom] > max(100, feature_df[metric.denom].quantile(0.25))
                ]
                try:
                    partition, _ = perform_test_on_df(
                        df=feature_df,
                        group_column="feature_value",
                        metric_column=str(metric),
                        test_func=kruskal,
                        test_func_kwargs={"nan_policy": "omit"},
                        pd_feature_func="median",
                    )

                except Exception:
                    continue

                if len(partition) > 1:
                    significance_table.loc[len(significance_table)] = {
                        "feature": get_frontend_name(feature),
                        "metric": get_frontend_name(metric),
                        "higher": partition[0],
                    }

            st.write("Statistically significant relationships")
            st.dataframe(significance_table.set_index("metric", drop=True).sort_index(), width=600)


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
