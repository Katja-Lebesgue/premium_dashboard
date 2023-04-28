import sys

sys.path.append("./.")
import inspect
import itertools
from statistics import mean

import numpy as np
import pandas as pd
from scipy.stats import (f_oneway, kruskal, levene, shapiro, ttest_ind,
                         ttest_ind_from_stats)

from src.statistics.bernoulli_tests import *
from src.statistics.get_binomial_sample import *
from src.utils.common import nan_to_none, none_to_unknown
from src.utils.decorators import print_execution_time


def mean_test_bernoulli(groups_df: dict, convert_nan_to_none: bool = False) -> dict:

    # remove empties
    groups_df = groups_df[groups_df["size"] > 3]

    if convert_nan_to_none:
        p = None
    else:
        p = np.nan

    result = {"p": p}

    if len(groups_df) == 0:
        return result

    groups_df["mean"] = groups_df.apply(lambda df: df.positive / df["size"], axis=1)

    print(groups_df)

    for group in groups_df.index:
        result[none_to_unknown(group)] = {
            "mean": groups_df.loc[group, "mean"],
            "size": groups_df.loc[group, "size"],
        }

    if len(groups_df) < 2:
        return result

    positives = list(groups_df.positive)
    sizes = list(groups_df["size"])
    there_is_positive = any(groups_df.positive > 0)
    there_is_negative = any(groups_df.positive < groups_df["size"])
    there_is_both = there_is_positive and there_is_negative

    if not there_is_both:
        return result

    stat_levene, p_levene = levene_bernoulli(positives=positives, sizes=sizes)
    equal_var = p_levene > 0.1

    if len(groups_df) == 2:
        stat, p = ttest_bernoulli(positives=positives, sizes=sizes, equal_var=equal_var)
        test_type = "t"

    else:
        if equal_var:
            stat, p = f_oneway_bernoulli(positives=positives, sizes=sizes)
            test_type = "anova"
        else:
            stat, p = chi2_contingency_bernoulli(positives=positives, sizes=sizes)
            test_type = "chi2"

    if convert_nan_to_none:
        stat, p, stat_levene, p_levene = (nan_to_none(x) for x in (stat, p, stat_levene, p_levene))

    result = {
        "stat": stat,
        "p": p,
        "test_type": test_type,
        "stat_levene": stat_levene,
        "p_levene": p_levene,
    }

    for group in groups_df.index:
        result[none_to_unknown(group)] = {
            "mean": groups_df.loc[group, "mean"],
            "size": groups_df.loc[group, "size"],
        }

    significant = p < 0.1

    result["conclusion"] = "significant" if significant else "insignificant"

    result["winner"] = groups_df.idxmax()["mean"] if significant else None

    return result


def mean_test_bernoulli_ctr(df: pd.DataFrame, group_col: str, convert_nan_to_none: bool = False):

    groups_df = create_groups_df(df=df, group_col=group_col, size_col="impr", positive_col="link_clicks")

    result = mean_test_bernoulli(groups_df=groups_df, convert_nan_to_none=convert_nan_to_none)

    return result


def mean_test_bernoulli_cr(df: pd.DataFrame, group_col: str, convert_nan_to_none: bool = False):

    groups_df = create_groups_df(df=df, group_col=group_col, size_col="link_clicks", positive_col="purch")

    result = mean_test_bernoulli(groups_df=groups_df, convert_nan_to_none=convert_nan_to_none)

    return result


def create_groups_df(df: pd.DataFrame, group_col: str, size_col: str, positive_col: str) -> pd.DataFrame:

    df[group_col] = df[group_col].fillna("unknown")

    values = df[group_col].value_counts(dropna=False).index

    groups_df = pd.DataFrame(0, index=values, columns=["positive", "size"])

    for value in values:
        filtered_df = df[df[group_col] == value]
        size = filtered_df[size_col].sum()
        positive = filtered_df[positive_col].sum()
        groups_df.loc[value, "positive"] = positive
        groups_df.loc[value, "size"] = size

    return groups_df


def to_series(x):
    return pd.Series(x)


def main():
    positives = [100, 1118]
    sizes = [1000, 1270]
    samples = [get_binomial_sample(positive=positive, size=size) for positive, size in zip(positives, sizes)]

    groups_df = pd.DataFrame(
        np.transpose([positives, sizes]),
        columns=["positive", "size"],
        index=["a", "b"],
    )

    result = mean_test_bernoulli(groups_df=groups_df)
    print(result)
    # f, p = levene(*samples)
    # print(f"pravi: {[f, p]}")


if __name__ == "__main__":
    main()
