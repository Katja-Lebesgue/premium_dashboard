import sys

sys.path.append("./.")
import pandas as pd
import itertools

from globals import *


def create_global_tests_analysis_table(df: pd.DataFrame) -> pd.DataFrame:

    for metric, test in itertools.product(metrics, tests):
        df[f"{test}_{metric}_statistically_significant"] = df[f"{test}_{metric}"].apply(
            is_significant
        )

    iterables = [metrics, tests, values]

    idx = pd.MultiIndex.from_product(iterables, names=["metric", "test", "value"])

    cols = pd.MultiIndex.from_product(iterables[1:], names=["test", "value"])

    table = pd.DataFrame(
        0,
        columns=cols,
        index=idx,
    )

    values = [True, False, None]

    for metric, test1, test2, value1, value2 in itertools.product(
        metrics, tests, tests, values, values
    ):
        count = len(
            df[
                (df[f"{test1}_{metric}_statistically_significant"].isin([value1]))
                & (df[f"{test2}_{metric}_statistically_significant"].isin([value2]))
            ]
        )
        table.loc[(metric, test1, value1), (test2, value2)] = count

    return table


def is_significant(test_result):
    jsons = [value for value in test_result.values() if type(value) == dict]
    p = test_result["p"]
    if len(jsons) < 2 or p is None:
        return None
    else:
        return p < 0.1
