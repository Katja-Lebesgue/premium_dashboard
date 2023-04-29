import sys

sys.path.append("./.")

import warnings
from math import sqrt

import numpy as np
import pandas as pd
from scipy.stats import norm
from statsmodels.stats.proportion import proportion_confint, proportions_ztest

from src.utils import *


# @print_execution_time
def proportion_test(positive1, size1, positive2, size2, convert_nan_to_none: bool = False):
    p1 = positive1 / size1 if size1 else np.nan
    p2 = positive2 / size2 if size2 else np.nan

    n1 = size1
    n2 = size2

    z_stat, p_value = (np.nan, np.nan)

    if not (size1 and size2) or not (positive1 or positive2):
        pass
    else:
        z_stat, p_value = proportions_ztest(count=[positive1, positive2], nobs=[size1, size2])

    if convert_nan_to_none:
        p1, p2, n1, n2, z_stat, p_value = (nan_to_none(x) for x in (p1, p2, n1, n2, z_stat, p_value))

    result = {
        "stat": z_stat,
        "p": p_value,
        "test_type": "proportion",
        True: {"mean": p1, "size": n1},
        False: {"mean": p2, "size": n2},
    }

    return result


def proportion_test_cr(
    group1: pd.DataFrame, group2: pd.DataFrame, convert_nan_to_none: bool = False
) -> float:
    positive1 = group1.purch.sum()
    size1 = group1.link_clicks.sum()
    positive2 = group2.purch.sum()
    size2 = group2.link_clicks.sum()

    result = proportion_test(
        positive1=positive1,
        size1=size1,
        positive2=positive2,
        size2=size2,
        convert_nan_to_none=convert_nan_to_none,
    )

    return result


def proportion_test_ctr(
    group1: pd.DataFrame, group2: pd.DataFrame, convert_nan_to_none: bool = False
) -> float:
    positive1 = group1.link_clicks.sum()
    size1 = group1.impr.sum()
    positive2 = group2.link_clicks.sum()
    size2 = group2.impr.sum()

    result = proportion_test(
        positive1=positive1,
        size1=size1,
        positive2=positive2,
        size2=size2,
        convert_nan_to_none=convert_nan_to_none,
    )

    return result


if __name__ == "__main__":
    a = np.random.binomial(1, 0.2123, 6180)
    b = np.random.binomial(1, 0.2462, 853)
    positive1 = np.sum(a)
    positive2 = np.sum(b)
    size1 = len(a)
    size2 = len(b)
    result = proportion_test(positive1, size1, positive2, size2)
    # print(result["p"])
    print(proportion_test(5, 83, 12, 99)["p"])
