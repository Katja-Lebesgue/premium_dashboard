import os
import re
from datetime import datetime
from uuid import uuid1

import numpy as np
import pandas as pd
import streamlit as st
from dateutil.relativedelta import relativedelta

from src.app.frontend_names import get_frontend_name
from src.app.utils import *
from src.app.utils.css import *
from src.app.utils.filter_df import FilterType, filter_df
from src.app.utils.labels_and_values import *
from src.database.session import db
from src.models.enums.facebook import BOOLEAN_TEXT_FEATURES
from src.pingers import ping_facebook_creative_and_performance
from src.statistical_tests.proportion_test import *
from src.utils import *


def shop_custom_performance_test(shop_id: int):
    data_shop = st_cache_data(
        _func=ping_facebook_creative_and_performance,
        func_name=ping_facebook_creative_and_performance.__name__,
        shop_id=shop_id,
        _db=db,
    )

    if not len(data_shop):
        st.warning("No data")
        return

    _, col1, _ = st.columns([1, 4, 1])

    # min_date = data_shop.year_month.min().to_pydatetime()
    # max_date = data_shop.year_month.max().to_pydatetime()
    # default_min_date = max(min_date, max_date - relativedelta(months=24))

    # with col1:
    #     start_date, end_date = st.select_slider(
    #         label="Choose time period:",
    #         value=(default_min_date, max_date),
    #         key="a",
    #         options=sorted(data_shop.year_month.unique().tolist()),
    #         format_func=lambda datetime_: datetime_.strftime("%Y-%m"),
    #     )

    #     data_shop = data_shop[data_shop.year_month.between(start_date, end_date)]

    test_group1 = data_shop

    test_group2 = data_shop.copy()

    col1, col2 = st.columns(2)

    with col1:
        st.header("Group 1")
        test_group1 = filter_basic_features(test_group1, "1")
        test_group1 = filter_text_features(test_group1, "1")
        st.info(f"Total of {test_group1.ad_id.nunique()} ads filtered.")

    with col2:
        st.header("Group 2")
        test_group2 = filter_basic_features(test_group2, "2")
        test_group2 = filter_text_features(test_group2, "2")
        st.info(f"Total of {test_group2.ad_id.nunique()} ads filtered.")

    if len(test_group1) or len(test_group2):
        test_table = create_test_table(test_group1, test_group2)
        test_table_style = style_test_table(test_table)

        _, col, _ = st.columns([1, 3, 1])

        with col:
            st.write(test_table_style.to_html(escape=False), unsafe_allow_html=True)

    return


def filter_basic_features(df: pd.DataFrame, group_id: str) -> pd.DataFrame:
    st.subheader("Filter basic features")
    default_min_date = df.year_month.max() - relativedelta(months=24)
    df = filter_df(
        df=df,
        column_name="year_month",
        filter_type=FilterType.slider,
        selecter_id=group_id,
        slider_default_lower_bound=default_min_date,
    )
    df = filter_df(df=df, column_name="target", filter_type=FilterType.checkbox, selecter_id=group_id)
    df = filter_df(df=df, column_name="creative_type", filter_type=FilterType.checkbox, selecter_id=group_id)

    return df


def filter_text_features(df: pd.DataFrame, group_id: str) -> pd.DataFrame:
    st.subheader("Filter text features")

    for feature in BOOLEAN_TEXT_FEATURES:
        df = filter_df(df=df, column_name=feature, filter_type=FilterType.checkbox, selecter_id=group_id)

    return df


def create_test_table(group_true: pd.Series, group_false: pd.Series) -> pd.DataFrame:
    table = pd.DataFrame(
        columns=["spend", "impr", "clicks", "ctr", "cr"],
        index=["group 1", "group 2", "p-value"],
    )

    pvalue = [np.nan, np.nan, np.nan]

    result_ctr = proportion_test_ctr(group1=group_true, group2=group_false)
    result_cr = proportion_test_cr(group1=group_true, group2=group_false)

    pvalue.extend([result_ctr["p"], result_cr["p"]])

    table.loc["group 1", :] = [
        group_true.spend.sum(),
        group_true.impr.sum(),
        group_true.clicks.sum(),
        result_ctr[True]["mean"] if True in result_ctr.keys() else np.nan,
        result_cr[True]["mean"] if True in result_ctr.keys() else np.nan,
    ]
    table.loc["group 2", :] = [
        group_false.spend.sum(),
        group_false.impr.sum(),
        group_false.clicks.sum(),
        result_ctr[False]["mean"] if False in result_ctr.keys() else np.nan,
        result_cr[False]["mean"] if False in result_ctr.keys() else np.nan,
    ]

    table.loc["p-value", :] = pvalue

    return table


def style_test_table(df: pd.DataFrame) -> pd.DataFrame.style:
    # style small p-values
    slice = (["p-value"], df.columns)
    df_style = df.style.applymap(style_small_values, props="color: red", subset=slice)

    # add bars
    slice = (["group 1", "group 2"], df.columns)
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
