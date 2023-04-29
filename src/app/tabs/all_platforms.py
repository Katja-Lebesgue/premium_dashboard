import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from loguru import logger
from plotly.subplots import make_subplots

from src.app.utils.css import GREEN, hide_dataframe_row_index
from src.database.session import db
from src.models.enums.EPlatform import PLATFORMS, EPlatform
from src.pingers import ping_ads_insights_all_platforms
from src.utils import *


def all_platforms():
    st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
    df = st_ping_ads_insights(get_industry=True, columns=["spend", "revenue"])
    df = df[~df.shop_id.isin([50517862, 39831581])]

    df = df.groupby(["shop_id", "year_month", "industry"]).sum().reset_index()
    shop_size = (
        df.groupby(["shop_id"])
        .mean()["total_revenue"]
        .reset_index()
        .rename(columns={"total_revenue": "mean_monthly_revenue"})
    )
    df = df.merge(shop_size, on="shop_id")
    df = df[(df.total_spend != 0) & (df.mean_monthly_revenue != 0) & (df.shop_id != 50517862)]

    q = 4
    df["shop_size"], bins = pd.qcut(
        df.mean_monthly_revenue, q=q, labels=list(range(q)), retbins=True, duplicates="drop"
    )
    df.shop_size = df.shop_size.astype(int)
    display_spend_statistics(df=df, bins=bins)

    col_breakdown1, col_breakdown2 = st.columns(2)

    with col_breakdown1:
        st.write("Choose shop size:")
        shop_size_filter = []
        for shop_size in sorted(df.shop_size.unique()):
            check = st.checkbox(
                f"${big_number_human_format(bins[shop_size])}-${big_number_human_format(bins[shop_size+1])}",
                value=True,
            )
            if check:
                shop_size_filter.append(shop_size)

        df = df.loc[df.shop_size.isin(shop_size_filter)]

        industry = st.selectbox(label="Choose industry:", options=["all"] + list(df.industry.unique()))

        if industry != "all":
            df = df[df.industry == industry]

    with col_breakdown2:
        display_platform_table(df=df)
        display_combinations_table(df=df)

    platform_spend_through_time(df=df)


@st.experimental_memo
def st_ping_ads_insights(**kwargs):
    return ping_ads_insights_all_platforms(db=db, **kwargs)


def display_spend_statistics(df: pd.DataFrame, bins=list[float]):
    st.header(f"Total marketing budget: {big_number_human_format(df.total_spend.sum())}")
    df = df.groupby(["shop_id", "industry"]).mean().reset_index()
    col_budget1, col_budget2 = st.columns(2)

    fig = go.Figure(
        data=go.Scatter(
            x=df.loc[df.total_spend < 300000, "total_spend"],
            y=df.loc[df.total_revenue < 2000000, "total_revenue"],
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
            go.Box(x=df.loc[df.industry == industry, "total_spend"], boxpoints=False, name=industry)
        )

    fig.update_layout(showlegend=False, title="Monthly budget by industry", xaxis_title="monthly budget")
    with col_budget2:
        st.plotly_chart(fig)


def display_platform_table(df: pd.DataFrame):
    # backend
    table = pd.DataFrame(columns=["platform", "shops (%)", "total spend", "median monthly spend"])
    num_shops = df.shop_id.nunique()

    for platform in PLATFORMS:
        filtered = df.loc[df[f"{platform}_spend"] > 0, :]
        shops = filtered.shop_id.nunique()
        shops_prc = shops / num_shops
        spend = filtered[f"{platform}_spend"].sum()
        monthly_spend = filtered.groupby(["shop_id", "industry"]).median()[f"{platform}_spend"].median()
        row = {
            "platform": platform,
            # "shops": shops,
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


def display_combinations_table(df: pd.DataFrame):
    df = df.groupby(["shop_id", "industry"]).sum().copy()

    table = pd.DataFrame(columns=["combination", "shops", "budget_split"])
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

    # # centering text in columns, doesn't work
    # table_style = table_style.set_properties(subet=["combination"], **{"text-align": "center"})
    # table_style = table_style.set_table_styles([dict(selector="th", props=[("text-align", "center")])])

    table_style.format(
        formatter={
            "combination": format_combination_column,
            "shops": lambda x: "{:,.2f}%".format(x * 100),
            "budget_split": lambda x: "-".join([str(int(y * 100)) for y in x]) if len(x) > 1 else "-",
        },
    )
    st.write("Breakdown by platform combinations")
    st.dataframe(table_style)


def format_combination_column(combination: list[str]) -> str:
    if len(combination) == 1:
        return f"{str(combination[0]).capitalize()} only"

    return " & ".join([platform.capitalize() for platform in combination])


def get_spend_ratio(s: pd.Series, platforms: list):
    ratio = [s[f"{platform}_spend"] / s.total_spend for platform in platforms]
    return ratio


def get_data_by_platform_combination(df: pd.DataFrame, combination: list, platforms: list) -> dict | None:
    filter = [True in range(len(df))]

    for platform in platforms:
        if platform in combination:
            filter = filter & (df[f"{platform}_spend"] > 0)
        else:
            filter = filter & (df[f"{platform}_spend"] == 0)
    filtered = df[filter].copy()
    if not len(filtered):
        logger.debug(f"empty combination: {combination}")
        return None
    platforms_without_the_last_one = combination[: len(combination) - 1]
    filtered["spend_ratio"] = filtered.apply(
        lambda df: get_spend_ratio(df, platforms=platforms_without_the_last_one), axis=1
    )
    mean_ratio = np.mean(filtered["spend_ratio"].tolist(), axis=0)

    result = {
        "combination": combination,
        "shops": len(filtered) / len(df),
        "budget_split": list(mean_ratio) + [1 - mean_ratio.sum()],
    }
    return result


def platform_spend_through_time(df: pd.DataFrame):
    col1, col2 = st.columns([1, 3])

    with col1:
        metric = st.selectbox(
            "Select metric",
            ("spend", "revenue"),
            key="metric",
        )

        df = df.rename(
            columns={f"{platform}_{metric}": f"{platform}" for platform in get_enum_values(EPlatform)}
        )
        df = df[["year_month", "shop_id"] + get_enum_values(EPlatform)]

        total_or_shop = st.select_slider("Choose wisely", ("Total", "Shop average"), value="Total")

        if total_or_shop == "Shop average":
            df = (
                df.set_index(["year_month", "shop_id"])
                .div(df.groupby(["year_month", "shop_id"]).sum())
                .reset_index()
            )

        a = df.groupby(["year_month"]).sum()[get_enum_values(EPlatform)].unstack()
        a = (
            a.reset_index()
            .rename(columns={"level_0": "platform", 0: "value"})
            .set_index(["year_month", "platform"])
        )

        bar_height = st.select_slider("Adjust bar height", ("Absolute", "Relative"), value="Relative")

        if bar_height == "Relative":
            monthly = a.reset_index().groupby("year_month").sum()
            a = a / monthly

        a = pd.DataFrame(a).reset_index()

    with col2:
        fig = px.bar(
            a,
            x="year_month",
            y="value",
            color="platform",
            title="value",
        )

        fig.update_layout(barmode="stack")

        st.plotly_chart(fig)
