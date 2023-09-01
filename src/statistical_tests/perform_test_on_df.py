from typing import Callable

import pandas as pd
from scipy.stats import kruskal


def perform_test_on_df(
    df: pd.DataFrame,
    group_column: str,
    metric_column: str,
    test_func: Callable = kruskal,
    test_func_kwargs: dict = {"nan_policy": "omit"},
    pd_feature_func: str = "median",
):
    grouped_df = df.groupby(group_column)[metric_column]
    sorted_groups = getattr(grouped_df, pd_feature_func)().sort_values(ascending=False).index.tolist()
    pvalue_df = pd.DataFrame(columns=sorted_groups, index=sorted_groups)
    partition = []
    current_slice = [sorted_groups[0]]
    for better_group, worse_group in zip(sorted_groups[:-1], sorted_groups[1:]):
        better_sample = grouped_df.get_group(better_group)
        worse_sample = grouped_df.get_group(worse_group)
        pvalue = test_func(better_sample, worse_sample, **test_func_kwargs).pvalue
        pvalue_df.loc[better_group, worse_group] = pvalue
        if pvalue < 0.1:
            partition.append(current_slice)
            current_slice = []
        current_slice.append(worse_group)
    partition.append(current_slice)
    return partition, pvalue_df
