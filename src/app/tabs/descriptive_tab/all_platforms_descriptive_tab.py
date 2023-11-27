from typing import Literal
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from loguru import logger
from plotly.subplots import make_subplots

from src.app.utils.css import GREEN, hide_dataframe_row_index
from src.database.session import db
from src.models.enums.EPlatform import EPlatform
from src.pingers.ping_ads_insights import ping_ads_insights_all_platforms, PLATFORMS
from src.utils import *
from src.app.utils import filter_df, FilterType
from src.app.tabs.descriptive_tab.descriptive_tab import DescriptiveTab


class AllPlatformsDescriptiveTab(DescriptiveTab):
    metric_columns = [
        "spend_USD",
        "impr",
        "clicks",
        "purch",
        "purch_value_USD",
    ]

    @property
    def descriptive_columns(self) -> list[str]:
        return ["platform"]

    @property
    def pie_columns(self) -> list[str]:
        return super().pie_columns

    @property
    def tag(self) -> str:
        return super().tag

    def show(self):
        st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
        df = self.ping_ads_insights(_db=db, get_industry=True)

        df = filter_df(
            df=df,
            column_name="year_month",
            filter_type=FilterType.select_slider,
            format_func=lambda date_time: date_time.strftime("%Y-%m"),
            slider_default_lower_bound=datetime(year=2015, month=1, day=1),
            selecter_id="1",
        )

        # df = (
        #     df.groupby(["shop_id", "year_month", "industry", "feature", "feature_value"])[self.metric_columns]
        #     .sum()
        #     .reset_index()
        # )

        shop_size = (
            df.groupby(["shop_id"])["purch_value_USD"]
            .mean()
            .reset_index()
            .rename(columns={"purch_value_USD": "mean_monthly_revenue"})
        )
        df = df.merge(shop_size, on="shop_id")
        df = df[(df.spend_USD != 0) & (df.mean_monthly_revenue > 0)]

        q = 4
        df["shop_size"], bins = pd.qcut(
            df.mean_monthly_revenue, q=q, labels=list(range(q)), retbins=True, duplicates="drop"
        )
        df.shop_size = df.shop_size.astype(int)
        self.display_spend_statistics(df=df, bins=bins)

        col_breakdown1, col_breakdown2 = st.columns(2)

        with col_breakdown1:
            st.write("Choose shop size:")
            shop_size_filter = []
            for shop_size in sorted(df.shop_size.unique()):
                check = st.checkbox(
                    f"\${big_number_human_format(bins[shop_size], big_decimals=0)} - \${big_number_human_format(bins[shop_size+1], big_decimals=0)}",
                    value=True,
                )
                if check:
                    shop_size_filter.append(shop_size)

            df = df.loc[df.shop_size.isin(shop_size_filter)]

            industry = st.selectbox(label="Choose industry:", options=["all"] + list(df.industry.unique()))

            if industry != "all":
                df = df[df.industry == industry]

            st.info(f"Total of {df.shop_id.nunique() * 7} shops selected.")

        with col_breakdown2:
            self.display_platform_table(df=df)
            self.display_combinations_table(df=df)

        summary_df = (
            df.groupby(["year_month", "feature", "feature_value"])[self.metric_columns].sum().reset_index()
        )

        self.descriptive_features_through_time(summary_df=summary_df)

        self.benchmarks(main_df=df)

    @st.cache_data
    def ping_ads_insights(
        _self,
        _db: Session,
        get_industry: bool = True,
    ):
        metric_columns = [col.removesuffix("_USD") for col in _self.metric_columns]
        df = ping_ads_insights_all_platforms(db=_db, get_industry=get_industry, columns=metric_columns)
        df = df[~df.shop_id.isin([50517862, 39831581, 123481234])]
        df["feature"] = "platform"
        df = df.rename(columns={"platform": "feature_value"})
        for metric in _self.metrics:
            df[str(metric)] = df.apply(metric.formula_series, axis=1)
        return df

    def display_spend_statistics(self, df: pd.DataFrame, bins=list[float]):
        st.header(f"Total marketing budget: ${big_number_human_format(df.spend_USD.sum())}")
        df = df.groupby(["shop_id", "industry"]).mean(numeric_only=True).reset_index()
        col_budget1, col_budget2 = st.columns(2)

        fig = go.Figure(
            data=go.Scatter(
                x=df.loc[df.spend_USD < 300000, "spend_USD"],
                y=df.loc[df.purch_value_USD < 2000000, "purch_value_USD"],
                mode="markers",
                # labels={"total_revenue": "monthly revenue", "total_spend": "monthly budget"},
                # range_y=(0, 2000000),
                # title="Monthly revenue by budget",
            )
        )
        fig.update_layout(
            showlegend=False,
            title="Monthly revenue by budget",
            xaxis_title="monthly budget",
            yaxis_title="monthly revenue",
        )

        with col_budget1:
            st.plotly_chart(fig)

        # fig = px.box(df, x="industry", y="total_spend", points="all")

        fig = go.Figure()
        industries = list(df.industry.unique())
        industries.remove("unknown")
        for industry in industries:
            fig.add_trace(
                go.Box(x=df.loc[df.industry == industry, "spend_USD"], boxpoints=False, name=industry)
            )

        fig.update_layout(showlegend=False, title="Monthly budget by industry", xaxis_title="monthly budget")
        with col_budget2:
            st.plotly_chart(fig)

    def display_platform_table(self, df: pd.DataFrame):
        # backend
        table = pd.DataFrame(columns=["platform", "shops (%)", "total spend", "median monthly spend"])
        num_shops = df.shop_id.nunique()

        platform_df = df[df.feature == "platform"]

        for platform in PLATFORMS:
            filtered = platform_df[(platform_df.feature_value == platform.name) & (platform_df.spend_USD > 0)]
            shops = filtered.shop_id.nunique()
            shops_prc = shops / num_shops
            spend = filtered["spend_USD"].sum()
            monthly_spend = filtered.groupby(["shop_id", "industry"])["spend_USD"].median().median()
            row = {
                "platform": platform.name,
                "shops (%)": shops_prc,
                "total spend": spend,
                "median monthly spend": monthly_spend,
            }
            table.loc[len(table), :] = row

        # frontend
        table = table.sort_values(by="shops (%)", ascending=False)
        table_style = table.style.bar(color=GREEN, subset=["shops (%)"], vmax=1)
        table_style = table_style.bar(color=GREEN, subset=["total spend", "median monthly spend"])
        table_style.format(
            formatter={
                "shops (%)": lambda x: "{:,.2f}%".format(x * 100),
                "total spend": lambda x: f"${big_number_human_format(x)}",
                "median monthly spend": lambda x: f"${big_number_human_format(x)}",
            },
        )
        st.write("Breakdown by platform")
        st.dataframe(table_style)

    def display_combinations_table(self, df: pd.DataFrame):
        df = df[df.feature == "platform"]
        df = (
            df.groupby(["shop_id", "feature_value"])[["spend_USD"]]
            .sum()
            .unstack(level="feature_value")
            .loc[:, "spend_USD"]
        )
        df = df.fillna(0)
        df["total"] = df.apply(lambda s: sum([s[platform.name] for platform in PLATFORMS]), axis=1)

        table = pd.DataFrame(columns=["combination", "shops", "total_spend", "budget_split"])
        platform_combinations = get_all_subsets(PLATFORMS)

        # backend
        for combination in platform_combinations:
            if not len(combination):
                continue
            row = get_data_by_platform_combination(df=df, combination=combination, platforms=PLATFORMS)
            if row is not None:
                table.loc[len(table), :] = row

        # frontend
        table = table.sort_values(by="shops", ascending=False)
        table_style = table.style.bar(color=GREEN, subset=["shops"], vmax=1)

        table_style = table_style.set_properties(subet=["combination"], **{"text-align": "center"})
        table_style = table_style.set_table_styles([dict(selector="th", props=[("text-align", "center")])])

        table_style.format(
            formatter={
                "combination": format_combination_column,
                "shops": lambda x: "{:,.2f}%".format(x * 100),
                "total_spend": lambda x: big_number_human_format(x),
                "budget_split": lambda x: "-".join([str(round(y * 100)) for y in x]) if len(x) > 1 else "-",
            },
        )
        st.write("Breakdown by platform combinations")
        st.write(table_style.to_html(escape=False), unsafe_allow_html=True)


def format_combination_column(combination: list[str]) -> str:
    if len(combination) == 1:
        return f"{str(combination[0]).capitalize()} only"

    return " & ".join([platform.capitalize() for platform in combination])


def get_spend_ratio(s: pd.Series, platforms: list):
    ratio = [s[platform.name] / s["total"] for platform in platforms]
    return ratio


def get_data_by_platform_combination(df: pd.DataFrame, combination: list, platforms: list) -> dict | None:
    filter = [True in range(len(df))]

    for platform in platforms:
        if platform in combination:
            filter = filter & (df[platform.name] > 0)
        else:
            filter = filter & (df[platform.name] == 0)
    filtered = df[filter]
    if not len(filtered):
        logger.debug(f"empty combination: {combination}")
        return None
    platforms_without_the_last_one = combination[: len(combination) - 1]
    filtered["spend_ratio"] = filtered.apply(
        lambda df: get_spend_ratio(df, platforms=platforms_without_the_last_one), axis=1
    )
    mean_ratio = np.mean(filtered["spend_ratio"].tolist(), axis=0)

    result = {
        "combination": [platform.name for platform in combination],
        "shops": len(filtered) / len(df),
        "total_spend": filtered.total.sum(),
        "budget_split": list(mean_ratio) + [1 - mean_ratio.sum()],
    }
    return result


all_platforms_descriptive_tab = AllPlatformsDescriptiveTab()
