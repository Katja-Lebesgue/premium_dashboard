from scipy.stats import ttest_ind_from_stats

from src.statistical_tests import *


def ttest_bernoulli(positives: list, sizes: list, equal_var: bool = True) -> float:
    negatives = [size - positive for size, positive in zip(sizes, positives)]
    means = [positive / size for positive, size in zip(positives, sizes)]

    stds = [
        get_std(positive=positive, negative=negative, mean=mean)
        for positive, negative, mean in zip(positives, negatives, means)
    ]

    stat, p = ttest_ind_from_stats(
        mean1=means[0],
        mean2=means[1],
        std1=stds[0],
        std2=stds[1],
        nobs1=sizes[0],
        nobs2=sizes[1],
        equal_var=equal_var,
    )

    return stat, p


def get_std(positive: int, negative: int, mean: int):
    var = positive * (1 - mean) ** 2 + negative * mean**2
    var = var / (positive + negative - 1)
    std = sqrt(var)
    return std
