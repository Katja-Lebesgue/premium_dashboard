from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

from src.app.utils.css import *
from src.app.utils.labels_and_values import *
from src.statistics import *
from src.statistics.bernoulli_tests.mean_test_bernoulli import *
from src.statistics.mean_test import mean_test
from src.utils.common import *
from src.utils.common import big_number_human_format


def default_performance_tests(data_shop: pd.DataFrame):
    if not len(data_shop):
        st.warning("No data")
        return

    col1, col2, col3 = st.columns([1, 1, 2])

    min_date = data_shop.year_month.min().to_pydatetime()
    max_date = datetime.today()

    with col1:
        timeperiod = st.slider(
            label="Choose time period:",
            value=(min_date, max_date),
            format="MM/DD/YYYY",
        )

        data_shop = data_shop[data_shop.year_month > timeperiod[0]]

    with col2:
        targeting = st.radio(
            "Select targets",
            tuple(targeting_dict.keys()),
            format_func=lambda x: targeting_dict[x],
            key="pie_targeting",
            index=2,
        )

        if targeting in ["targets_US", "targets_english"]:
            data_shop = data_shop.loc[data_shop[targeting] == True, :]

        st.write("Choose target:")

        target_filter = []

        for target in data_shop.target.unique():
            check = st.checkbox(str(target), value=True)
            if check:
                target_filter.append(target)

        data_shop = data_shop.loc[data_shop.target.isin(target_filter)]

    with col1:
        st.write(f"Total of {len(data_shop.ad_id.unique())} ads filtered.")

    if not len(target_filter) or not len(data_shop):
        return

    with col3:
        st.write("Promotional")
        promotion_table = create_test_table(df=data_shop, group_col="discounts_any")
        promotion_table_style = style_test_table(promotion_table)
        st.dataframe(promotion_table_style)

    st.empty()

    col3, col4 = st.columns(2)

    with col3:
        st.header("Promotional ads")

        data_promotional = data_shop.loc[data_shop.discounts_any == True, :]

        st.write(f"total of {data_promotional.ad_id.nunique()} promotional ads")

        if len(data_promotional):
            display_test_tables(df=data_promotional)

    with col4:
        st.header("Non-promotional ads")

        data_nonpromotional = data_shop.loc[data_shop.discounts_any == False, :]

        st.write(f"total of {data_nonpromotional.ad_id.nunique()} non-promotional ads")

        if len(data_nonpromotional):
            display_test_tables(df=data_nonpromotional)


def display_test_tables(df: pd.DataFrame):
    column_title_dict = {
        "emojis_any": "has emojis",
        "urgency_any": "creates urgency",
        "starts_with_question_any": "starts with a question",
        "user_addressing_any": "adresses user",
        "fact_words_any": "states facts",
        "prices_any": "mentions price",
    }

    for col, tit in column_title_dict.items():
        st.write(tit)
        test_table = create_test_table(df=df, group_col=col)
        if test_table.loc[:, ["ctr", "cr"]].count().sum():
            test_table_style = style_test_table(test_table)
            st.dataframe(test_table_style)
        else:
            st.write("Couldn't perform tests")

    st.write("Creative type")
    creative_type_test_table = create_creative_type_test_table(df)
    creative_type_test_table_style = style_test_table(creative_type_test_table)
    st.dataframe(creative_type_test_table_style)


def create_test_table(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    # initialize table
    table = pd.DataFrame(
        np.nan,
        columns=["spend", "impr", "clicks", "ctr", "cr"],
        index=["yes", "no", "p-value"],
    )

    pvalue = [np.nan, np.nan, np.nan]

    # divide groups
    group_true = df.loc[df[group_col].isin([True]), :].dropna(axis=0, subset=["ctr", "cr"])

    group_false = df.loc[df[group_col].isin([False]), :].dropna(axis=0, subset=["ctr", "cr"])

    result_ctr = mean_test_bernoulli_ctr(df=df, group_col=group_col, convert_nan_to_none=True)
    result_cr = mean_test_bernoulli_cr(df=df, group_col=group_col, convert_nan_to_none=True)

    pvalue.extend([result_ctr["p"], result_cr["p"]])

    table.loc["yes", :] = [
        group_true.spend.sum(),
        group_true.impr.sum(),
        group_true.link_clicks.sum(),
        result_ctr[True]["mean"] if True in result_ctr.keys() else np.nan,
        result_cr[True]["mean"] if True in result_cr.keys() else np.nan,
    ]
    table.loc["no", :] = [
        group_false.spend.sum(),
        group_false.impr.sum(),
        group_false.link_clicks.sum(),
        result_ctr[False]["mean"] if False in result_ctr.keys() else np.nan,
        result_cr[False]["mean"] if False in result_cr.keys() else np.nan,
    ]

    table.loc["p-value", :] = pvalue

    return table


def create_creative_type_test_table(df: pd.DataFrame) -> pd.DataFrame:
    values = ["image", "video", "carousel", "dynamic", "unknown"]

    table = pd.DataFrame(
        np.nan,
        columns=["spend", "impr", "clicks", "ctr", "cr"],
        index=values + ["p-value"],
    )

    pvalue = [np.nan, np.nan, np.nan]

    values = list(table.index)
    values.remove("p-value")

    result = dict()
    result["ctr"] = mean_test_bernoulli_ctr(df=df, group_col="creative_type")
    result["cr"] = mean_test_bernoulli_ctr(df=df, group_col="creative_type")

    for value in values:
        filtered_df = df[df.creative_type.isin([value])]
        table.loc[value, ["spend", "impr", "clicks"]] = [
            filtered_df.spend.sum(),
            filtered_df.impr.sum(),
            filtered_df.link_clicks.sum(),
        ]

    for metric in ["ctr", "cr"]:
        table.loc["p-value", metric] = result[metric]["p"]
        relevant_values = [value for value in values if value in result[metric].keys()]

        for value in relevant_values:
            table.loc[value, metric] = result[metric][value]["mean"]

    return table


def style_test_table(df: pd.DataFrame) -> pd.DataFrame.style:
    # style small p-values
    if "p-value" in df.index:
        slice = (["p-value"], df.columns)
        df_style = df.style.applymap(style_small_values, props="color: red", subset=slice)

    # add bars
    slice_x = list(df.index)

    if "p-value" in slice_x:
        slice_x.remove("p-value")

    slice = (slice_x, df.columns)
    df_style = df_style.bar(subset=slice, axis=0, width=70, color="#8BEDBE")

    # format percentages and dollars
    df_style.format(
        na_rep="-",
        precision=0,
        thousands=" ",
        formatter={
            "spend": lambda x: f"${big_number_human_format(int(x))}",
            "impr": big_number_human_format,
            "clicks": big_number_human_format,
            "ctr": lambda x: "{:,.2f}%".format(x * 100),
            "cr": lambda x: "{:.2f}%".format(x * 100),
            # ("p-value", "ctr"): "{:.2f}",
            # ("p-value", "cr"): "{:.2f}",
        },
    )

    # format p-values
    df_style.format(
        na_rep="-",
        formatter=lambda x: "{:.2f}".format(x) if x else x,
        subset=(["p-value"], df.columns),
    )

    return df_style
