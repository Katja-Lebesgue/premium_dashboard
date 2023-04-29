import os
import re
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

from src.app.utils.css import *
from src.app.utils.labels_and_values import *
from src.statistical_tests.proportion_test import *
from src.utils import *


def custom_performance_test(data_shop: pd.DataFrame):
    if not len(data_shop):
        st.warning("No data")
        return

    test_group1 = data_shop

    test_group2 = data_shop.copy()

    features = custom_feature_dict.keys()

    col1, col2 = st.columns(2)

    with col1:
        st.header("Group 1")
        test_group1 = group_filtering(test_group1, "1")
        test_group1 = feature_filtering(test_group1, features, "1")
        st.write(f"Total of {test_group1.ad_id.nunique()} ads filtered.")

    with col2:
        st.header("Group 2")
        test_group2 = group_filtering(test_group2, "2")
        test_group2 = feature_filtering(test_group2, features, "2")
        st.write(f"Total of {test_group2.ad_id.nunique()} ads filtered.")

    if len(test_group1) or len(test_group2):
        test_table = create_test_table(test_group1, test_group2)
        test_table = style_test_table(test_table)

        col3, col4, col5 = st.columns([1, 3, 1])

        with col4:
            st.dataframe(test_table)

    return


def group_filtering(df: pd.DataFrame, id: str) -> pd.DataFrame:
    st.subheader("Filter ad and target type")

    targeting = st.radio(
        "Country targets",
        tuple(targeting_dict.keys()),
        format_func=lambda x: targeting_dict[x],
        key=f"targeting_{id}",
        index=2,
    )

    if targeting in ["targets_US", "targets_english"]:
        df = df.loc[df[targeting] == True, :]

    for group in custom_group_dict.keys():
        filter = []

        with st.expander(f"{custom_group_dict[group]}"):
            for target in df[group].unique():
                check = st.checkbox(str(target), value=True, key=group + id)
                if check:
                    filter.append(target)

        df = df[df[group].isin(filter)]

    return df


def feature_filtering(df: pd.DataFrame, features: list[str], id: str) -> pd.DataFrame:
    st.subheader("Filter text features")

    for feature in features:
        filter = []

        with st.expander(f"{custom_feature_dict[feature]}"):
            if df[feature].unique() is not None:
                for target in df[feature].unique():
                    check = st.checkbox(str(target), value=True, key=feature + id)
                    if check:
                        filter.append(target)

                df = df[df[feature].isin(filter)]

            else:
                st.write("Nope")

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
        group_true.link_clicks.sum(),
        result_ctr[True]["mean"] if True in result_ctr.keys() else np.nan,
        result_cr[True]["mean"] if True in result_ctr.keys() else np.nan,
    ]
    table.loc["group 2", :] = [
        group_false.spend.sum(),
        group_false.impr.sum(),
        group_false.link_clicks.sum(),
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
