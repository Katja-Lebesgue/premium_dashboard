import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.app.utils.css import *
from src.app.utils.labels_and_values import *
from src.utils import *

load_dotenv()


files_dict = {
    "feature": "global_feature_tests_from_2021-06-03_to_2022-08-19.csv",
    "promotion": "global_promotion_tests_from_2021-06-03_to_2022-08-29.csv",
    "creative_type": "global_creative_type_tests_from_2021-06-03_to_2022-08-29.csv",
}


def market_performance_tests(
    global_data_s3_path: str = f"prljavo/",
):
    col1, col2 = st.columns(2)

    with col1:
        global_dates = get_global_dates()

        selected_date = st.selectbox(
            "Select time period",
            global_dates,
            format_func=lambda x: x.replace("_", " "),
        )

        # loading global test results from s3
        global_feature_tests_df = st_read_csv_from_s3(
            global_data_s3_path + "global_feature_tests_" + selected_date + ".csv"
        )

        global_promotion_tests_df = st_read_csv_from_s3(
            global_data_s3_path + "global_promotion_tests_" + selected_date + ".csv"
        )

        global_creative_type_tests_df = st_read_csv_from_s3(
            global_data_s3_path + "global_creative_type_tests_" + selected_date + ".csv"
        )

        # global_feature_tests_df = st_read_csv_from_s3(
        #     global_data_s3_path + files_dict["feature"]
        # )

        # global_promotion_tests_df = st_read_csv_from_s3(
        #     global_data_s3_path + files_dict["promotion"]
        # )

        # global_creative_type_tests_df = st_read_csv_from_s3(
        #     global_data_s3_path + files_dict["creative_type"]
        # )

        # target filtering
        target = st.radio("Select target", ("acquisition", "remarketing"))

        global_feature_tests_df = global_feature_tests_df.loc[global_feature_tests_df.target == target]

        global_promotion_tests_df = global_promotion_tests_df.loc[global_promotion_tests_df.target == target]

        global_creative_type_tests_df = global_creative_type_tests_df.loc[
            global_creative_type_tests_df.target == target
        ]

    with col2:
        st.write("Promotion test")

        promotion_table = create_test_table(global_promotion_tests_df)
        promotion_table_style = style_feature_test_table(promotion_table)
        st.dataframe(promotion_table_style)

    st.empty()

    col3, col4 = st.columns(2)

    with col3:
        st.header("Promotional ads")

        promotion_value = True

        feature_tests_promotional = global_feature_tests_df.loc[
            global_feature_tests_df.promotion == promotion_value, :
        ]

        creative_type_tests_promotional = global_creative_type_tests_df.loc[
            global_creative_type_tests_df.promotion == promotion_value, :
        ]

        if len(feature_tests_promotional):
            display_test_tables(
                global_feature_tests_df=feature_tests_promotional,
                global_creative_type_tests_df=creative_type_tests_promotional,
            )

        else:
            st.markdown("No promotional ads.")

    with col4:
        st.header("Non-promotional ads")

        promotion_value = False

        feature_tests_promotional = global_feature_tests_df.loc[
            global_feature_tests_df.promotion == promotion_value, :
        ]

        creative_type_tests_promotional = global_creative_type_tests_df.loc[
            global_creative_type_tests_df.promotion == promotion_value, :
        ]

        if len(feature_tests_promotional):
            display_test_tables(
                global_feature_tests_df=feature_tests_promotional,
                global_creative_type_tests_df=creative_type_tests_promotional,
            )

        else:
            st.markdown("No promotional ads.")


def get_global_dates(prefix: str = "prljavo/global_feature"):
    list_of_paths = list_objects_from_prefix(prefix=prefix)

    str_from_from = lambda x: x[x.find("from") : -4] if x.find("from") > -1 else None

    global_dates = [str_from_from(path) for path in list_of_paths if "done" not in path]

    global_dates = [date for date in global_dates if date]

    return global_dates


@st.experimental_memo
def st_read_csv_from_s3(*args, **kwargs):
    df = read_csv_from_s3(*args, **kwargs)

    df = rename_test_columns(df=df)

    return df


def rename_test_columns(df: pd.DataFrame) -> pd.DataFrame:
    find_substring_starting_with_test = lambda x: x[x.find("test") :]

    rename_dict = {col: find_substring_starting_with_test(col) for col in df.columns if "test" in col}

    df.rename(columns=rename_dict, inplace=True)

    return df


def display_test_tables(global_feature_tests_df: pd.DataFrame, global_creative_type_tests_df: pd.DataFrame):
    features = list(global_feature_tests_df.feature.unique())

    for feature in features:
        st.write(feature.replace("_", " "))
        filtered_df = global_feature_tests_df.loc[global_feature_tests_df.feature == feature, :]
        test_table = create_test_table(filtered_df)
        test_table_style = style_feature_test_table(test_table)
        st.dataframe(test_table_style)

    st.write("Creative type")
    creative_type_test_table = create_creative_type_test_table(global_creative_type_tests_df)
    creative_type_test_table_style = style_creative_type_test_table(creative_type_test_table)
    st.dataframe(creative_type_test_table_style)


def create_test_table(df: pd.DataFrame) -> pd.DataFrame:
    table = pd.DataFrame(
        columns=["ctr", "cr"],
        index=["positive", "neutral", "negative", "total shops in analysis"],
    )

    for metric in ["ctr", "cr"]:
        test_results = df["test_" + metric]
        total_shops = test_results.apply(lambda x: x["p"] is not None and x["p"] < 1).sum()
        table.loc["total shops in analysis", metric] = total_shops

        conclusions = test_results.apply(get_conclusion)

        for conclusion in ["positive", "neutral", "negative"]:
            total = (conclusions.isin([conclusion])).sum()
            prc = total / total_shops if total_shops else np.nan
            table.loc[conclusion, metric] = prc

    return table


def get_conclusion(test_result: dict) -> str:
    if test_result["stat"] is None or test_result["p"] == 1:
        return None
    p = test_result["p"]

    if p > 0.1:
        return "neutral"

    if True in test_result.keys() and test_result[True]["mean"] > test_result[False]["mean"]:
        return "positive"

    if (
        "group1" in test_result.keys()
        and "group2" in test_result.keys()
        and test_result["group1"]["mean"] is not None
        and test_result["group2"]["mean"] is not None
        and test_result["group1"]["mean"] > test_result["group2"]["mean"]
    ):
        return "positive"

    return "negative"


def create_creative_type_test_table(df: pd.DataFrame) -> pd.DataFrame:
    values = ["image", "video", "carousel", "dynamic", "unknown"]

    table = pd.DataFrame(
        columns=["ctr", "cr"],
        index=values + ["total shops in analysis"],
    )

    for metric in ["ctr", "cr"]:
        test_results = df["test_" + metric]
        winners = test_results.apply(get_winners)
        total_shops = test_results.apply(lambda x: x["p"] is not None).sum()
        table.loc["total shops in analysis", metric] = total_shops

        for value in values:
            total = winners.apply(lambda x: value in x).sum()
            prc = total / total_shops if total_shops else np.nan
            table.loc[value, metric] = prc

    return table


def get_winners(result: dict) -> list[str]:
    winners = []

    if result["p"] is None or result["p"] > 0.1:
        return winners

    # sorting means into Series
    means_dict = {
        k: result[k]["mean"] for k in result.keys() if type(result[k]) == dict and "mean" in result[k].keys()
    }
    means = pd.Series(means_dict)

    maxi = max(means)
    limit = maxi - 0.1 * maxi

    winners.extend(list(means[means > limit].index))

    return winners


def style_feature_test_table(df: pd.DataFrame) -> pd.DataFrame.style:
    df_style = df.style

    # add bars
    green = "#8BEDBE"
    yellow = "#F1F114"
    red = "#E76350"
    red = "#d65f5f"

    idx = ["positive", "neutral", "negative"]
    colors = [green, yellow, red]

    for target in ["ctr", "cr"]:
        target_max = df.loc[idx, target].max()
        for row, color in zip(idx, colors):
            df_style = df_style.bar(
                subset=(row, target),
                axis=0,
                width=70,
                color=color,
                vmin=0,
                vmax=target_max,
            )

    # format percentages
    df_style.format(
        na_rep="-",
        thousands=" ",
        formatter={
            "ctr": lambda x: "{:,.2f}%".format(x * 100),
            "cr": lambda x: "{:,.2f}%".format(x * 100),
        },
    )

    df_style.format(
        na_rep="-",
        formatter=lambda x: "{:.0f}".format(x) if x else x,
        subset=(["total shops in analysis"], df.columns),
    )

    return df_style


def style_creative_type_test_table(df: pd.DataFrame) -> pd.DataFrame.style:
    df_style = df.style

    # add bars
    green = "#8BEDBE"

    idx = list(df.index)
    idx.remove("total shops in analysis")
    colors = [green] * len(idx)

    for target in ["ctr", "cr"]:
        target_max = df.loc[idx, target].max()
        for row, color in zip(idx, colors):
            df_style = df_style.bar(
                subset=(row, target),
                axis=0,
                width=70,
                color=color,
                vmin=0,
                vmax=target_max,
            )

    # format percentages
    df_style.format(
        na_rep="-",
        # precision=0,
        thousands=" ",
        formatter={
            "ctr": lambda x: "{:,.2f}%".format(x * 100),
            "cr": lambda x: "{:,.2f}%".format(x * 100),
        },
    )

    df_style.format(
        na_rep="-",
        formatter=lambda x: "{:.0f}".format(x) if x else x,
        subset=(["total shops in analysis"], df.columns),
    )

    return df_style
