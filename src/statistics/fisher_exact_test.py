import numpy as np
import pandas as pd
from numpy import size
from scipy.stats import fisher_exact

from src.utils.common import nan_to_none
from src.utils.decorators import print_execution_time


@print_execution_time
def fisher_exact_test(
    group1: pd.DataFrame,
    group2: pd.DataFrame,
    positive_col: str,
    size_col: str,
    convert_nan_to_none: bool = False,
) -> float:

    table = pd.DataFrame(columns=["positive", "negative"])

    group1_positive = group1[positive_col].sum()
    group1_size = group1[size_col].sum()
    group1_negative = max(group1_size - group1_positive, 0)
    table.loc[0, :] = [group1_positive, group1_negative]

    group2_positive = group2[positive_col].sum()
    group2_size = group2[size_col].sum()
    group2_negative = max(group2_size - group2_positive, 0)
    table.loc[1, :] = [group2_positive, group2_negative]

    odsratio, p = fisher_exact(table)

    if p == 1:
        p = np.nan

    group1_mean = group1_positive / group1_size if group1_size else np.nan
    group2_mean = group2_positive / group2_size if group2_size else np.nan

    if convert_nan_to_none:
        odsratio, p, group1_mean, group2_mean = (nan_to_none(x) for x in (odsratio, p, group1_mean, group2_mean))

    result = {
        "stat": odsratio,
        "p": p,
        True: {"mean": group1_mean, "size": group1_size},
        False: {"mean": group2_mean, "size": group2_size},
    }

    return result


def fisher_exact_test_ctr(group1: pd.DataFrame, group2: pd.DataFrame, convert_nan_to_none: bool = False):
    result = fisher_exact_test(
        group1=group1,
        group2=group2,
        positive_col="link_clicks",
        size_col="impr",
        convert_nan_to_none=convert_nan_to_none,
    )
    return result


def fisher_exact_test_cr(group1: pd.DataFrame, group2: pd.DataFrame, convert_nan_to_none: bool = False):
    result = fisher_exact_test(
        group1=group1,
        group2=group2,
        positive_col="purch",
        size_col="link_clicks",
        convert_nan_to_none=convert_nan_to_none,
    )
    return result


def main():
    df = pd.DataFrame([[10000, 20000], [160, 300]], columns=["link_clicks", "impr"])
    df
    result = fisher_exact_test_ctr(
        group1=df.loc[0, :],
        group2=df.loc[df.link_clicks == 5],
    )
    print(result)


if __name__ == "__main__":
    main()
