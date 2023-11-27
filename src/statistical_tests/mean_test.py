import numpy as np
from scipy.stats import f_oneway, kruskal, levene, shapiro, ttest_ind

from src.statistical_tests.get_binomial_sample import *
from src.utils import *


def mean_test_ctr(df: pd.DataFrame, group_col: str, convert_nan_to_none: bool = False):
    samples_dict = create_samples_dict(
        df=df, group_col=group_col, size_col="impr", positive_col="link_clicks"
    )

    result = mean_test(
        samples_dict=samples_dict,
        convert_nan_to_none=convert_nan_to_none,
    )

    return result


def mean_test_cr(df: pd.DataFrame, group_col: str, convert_nan_to_none: bool = False):
    samples_dict = create_samples_dict(
        df=df, group_col=group_col, size_col="link_clicks", positive_col="purch"
    )

    result = mean_test(samples_dict=samples_dict, convert_nan_to_none=convert_nan_to_none)

    return result


def create_samples_dict(df: pd.DataFrame, group_col: str, size_col: str, positive_col: str):
    samples_dict = dict()

    values = df[group_col].value_counts(dropna=False).index

    for value in values:
        filtered_df = df[df[group_col] == value]
        size = filtered_df[size_col].sum()
        positive = filtered_df[positive_col].sum()
        sample = get_binomial_sample(size=size, positive=positive)
        samples_dict[value] = sample

    return samples_dict


def mean_test(samples_dict: dict, convert_nan_to_none: bool = False) -> dict:
    test_type = None

    stat, p, stat_levene, p_levene = [np.nan for i in range(4)]

    samples_dict = {
        none_to_unknown(group): [unit for unit in sample if unit is not None and not np.isnan(unit)]
        for group, sample in samples_dict.items()
        if len(sample)
    }

    samples_list = list(samples_dict.values())

    if len(samples_list) > 0:
        all_observations = sum(samples_list, [])

        if (
            len(samples_list) > 1
            and any([len(sample) > 1 for sample in samples_list])
            and len(set(all_observations)) > 1
        ):
            # equality of variance test
            stat_levene, p_levene = levene(*samples_list)

            # more than two groups
            if len(samples_list) > 2:
                # normality test
                if all([len(sample) > 3 for sample in samples_list]):
                    shapiro_pvalues = [shapiro(sample).pvalue for sample in samples_list]
                    p_shapiro = min(shapiro_pvalues)
                else:
                    p_shapiro = 0

                if p_levene > 0.1 and p_shapiro > 0.1:
                    stat, p = f_oneway(*samples_list)
                    test_type = "anova"
                else:
                    stat, p = kruskal(*samples_list, nan_policy="omit")
                    test_type = "kruskal"

            # two samples
            else:
                if p_levene > 0.1:
                    stat, p = ttest_ind(*samples_list, nan_policy="omit")
                    test_type = "t"

                else:
                    stat, p = kruskal(*samples_list, nan_policy="omit")
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
        result[group] = {"mean": np.nanmean(samples_dict[group]), "size": len(samples_dict[group])}

    return result
