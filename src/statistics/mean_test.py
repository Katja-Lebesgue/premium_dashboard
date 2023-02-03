from scipy.stats import levene, ttest_ind, kruskal, f_oneway, shapiro
import numpy as np
import pandas as pd
from statistics import mean

from src.utils.common import nan_to_none, none_to_unknown
from src.statistics.get_binomial_sample import *
from src.utils.decorators import print_execution_time
import itertools


@print_execution_time
def _mean(l):
    if type(l) == list:
        return np.mean(l)
    else:
        return l.mean()


@print_execution_time
def concat_lists(lists):
    if not len(lists):
        return []
    if type(lists[0]) == list:
        return list(itertools.chain(*lists))
    else:
        return pd.concat(lists)


@print_execution_time
def get_nunique(l):
    if type(l) == list:
        return len(set(l))
    else:
        return l.nunique()


@print_execution_time
def _levene(*args, **kwargs):
    result = levene(*args, **kwargs)
    return result


@print_execution_time
def _f_oneway(*args, **kwargs):
    result = f_oneway(*args, **kwargs)
    return result


@print_execution_time
def _shapiro(*args, **kwargs):
    result = shapiro(*args, **kwargs)
    return result


@print_execution_time
def _kruskal(*args, **kwargs):
    result = kruskal(*args, **kwargs)
    return result


@print_execution_time
def _ttest_ind(*args, **kwargs):
    result = ttest_ind(*args, **kwargs)
    return result


@print_execution_time
def mean_test(samples_dict: dict, convert_nan_to_none: bool = False) -> dict:

    # print(f"na_to_none: {convert_nan_to_none}")

    test_type = None

    stat, p, stat_levene, p_levene = [np.nan for i in range(4)]

    # samples_dict = {group: sample for group, sample in samples_dict.items()}

    samples_dict = {group: sample for group, sample in samples_dict.items() if len(sample)}

    samples_list = list(samples_dict.values())

    # print(f"len samples_list: {len(samples_list)}")

    if len(samples_list) > 0:

        all_observations = concat_lists(samples_list)

        if (
            len(samples_list) > 1
            and any([len(sample) > 1 for sample in samples_list])
            and get_nunique(all_observations) > 1
        ):

            stat_levene, p_levene = _levene(*samples_list)

            # multisamples
            if len(samples_list) > 2:

                if all([len(sample) > 3 for sample in samples_list]):
                    # print(
                    #     f"duljine uzoraka: {[sum(sample) for sample in samples_list]}"
                    # )
                    shapiro_pvalues = [_shapiro(sample).pvalue for sample in samples_list]
                    p_shapiro = min(shapiro_pvalues)
                else:
                    p_shapiro = 0

                if p_levene > 0.1 and p_shapiro > 0.1:
                    stat, p = _f_oneway(*samples_list)
                    test_type = "anova"
                else:
                    stat, p = _kruskal(*samples_list, nan_policy="omit")
                    test_type = "kruskal"

            # two samples
            else:

                if p_levene > 0.1:
                    stat, p = _ttest_ind(*samples_list, nan_policy="omit")
                    test_type = "t"

                else:
                    stat, p = _kruskal(*samples_list, nan_policy="omit")
                    test_type = "kruskal"

    if convert_nan_to_none:
        stat, p, stat_levene, p_levene = (nan_to_none(x) for x in (stat, p, stat_levene, p_levene))

    result = {
        "stat": stat,
        "p": p,
        "test_type": test_type,
        "stat_levene": stat_levene,
        "p_levene": p_levene,
    }

    for group in samples_dict.keys():
        result[none_to_unknown(group)] = {
            "mean": _mean(samples_dict[group]),
            "size": len(samples_dict[group]) if group in samples_dict.keys() else 0,
        }

    return result


def winners_and_losers(samples_dict: dict, convert_nan_to_none: bool = False) -> dict:

    mean_test_result = mean_test(samples_dict)

    result = {"winners": [], "losers": []}

    if mean_test_result["p"] > 0.1:
        return result

    # sorting means into Series
    means_dict = {
        k: mean_test_result[k]["mean"]
        for k in mean_test_result.keys()
        if type(mean_test_result[k]) == dict and "mean" in mean_test_result[k].keys()
    }
    means = pd.Series(means_dict)
    means = means.sort_values(ascending=False)
    means_len = len(means)

    print(f"means_len: {means_len}")

    if means_len < 2:
        return result

    result["winners"] = [means.index[0]]
    result["losers"] = [means.index[len(means) - 1]]

    means_len = len(means)

    # declaring winners
    p = 1
    upper_limit = 1

    while p > 0.1 and upper_limit < means_len:
        upper_limit = upper_limit + 1
        mean_test_result = mean_test(
            {group: sample for group, sample in samples_dict.items() if group in means.index[0:upper_limit]}
        )
        p = mean_test_result["p"]

    result["winners"].extend(list(means.index[1 : upper_limit - 1]))

    # declaring losers
    p = 1
    lower_limit = means_len - 1

    while p > 0.1 and lower_limit > 0:
        lower_limit = lower_limit - 1
        mean_test_result = mean_test(
            {group: sample for group, sample in samples_dict.items() if group in means.index[lower_limit:means_len]}
        )
        p = mean_test_result["p"]

    result["losers"].extend(list(means.index[lower_limit + 1 : means_len - 1]))

    return result


@print_execution_time
def mean_test_ctr(df: pd.DataFrame, group_col: str, convert_nan_to_none: bool = False):

    samples_dict = create_samples_dict(df=df, group_col=group_col, size_col="impr", positive_col="link_clicks")

    result = mean_test(
        samples_dict=samples_dict,
        convert_nan_to_none=convert_nan_to_none,
    )

    return result


@print_execution_time
def mean_test_cr(df: pd.DataFrame, group_col: str, convert_nan_to_none: bool = False):

    samples_dict = create_samples_dict(df=df, group_col=group_col, size_col="link_clicks", positive_col="purch")

    result = mean_test(samples_dict=samples_dict, convert_nan_to_none=convert_nan_to_none)

    return result


@print_execution_time
def create_samples_dict(df: pd.DataFrame, group_col: str, size_col: str, positive_col: str):

    samples_dict = dict()

    values = df[group_col].value_counts(dropna=False).index

    for value in values:
        filtered_df = df[df[group_col] == value]
        size = filtered_df[size_col].sum()
        positive = filtered_df[positive_col].sum()
        sample = get_binomial_sample(size=size, positive=positive)
        # sample = to_series(sample)
        samples_dict[value] = sample

    return samples_dict


@print_execution_time
def to_series(x):
    return pd.Series(x)
