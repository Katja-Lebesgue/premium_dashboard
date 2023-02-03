from statistics import mean
import sys

sys.path.append("././.")

from numpy import size
from scipy.stats import fisher_exact
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind_from_stats, ttest_ind

from src.utils.common import nan_to_none
from src.utils.decorators import print_execution_time
from src.statistics import *


def get_std(positive: int, negative: int, mean: int):
    var = positive * (1 - mean) ** 2 + negative * mean**2
    var = var / (positive + negative - 1)
    std = sqrt(var)
    return std


# @print_execution_time
def ttest_bernoulli(positives: list, sizes: list, equal_var: bool = True) -> float:

    negatives = [size - positive for size, positive in zip(sizes, positives)]
    means = [positive / size for positive, size in zip(positives, sizes)]

    stds = [
        get_std(positive=positive, negative=negative, mean=mean)
        for positive, negative, mean in zip(positives, negatives, means)
    ]

    # print(f"means: {means}")
    # print(f"stds: {stds}")

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


def main():
    positives = [100, 230]
    sizes = [200, 500]
    samples = [get_binomial_sample(positive=positive, size=size) for positive, size in zip(positives, sizes)]
    # print(samples)
    f_moj, p_moj = ttest_bernoulli(positives=positives, sizes=sizes)
    print(f"moji: {[f_moj, p_moj]}")
    f, p = ttest_ind(*samples)
    print(f"pravi: {[f, p]}")


if __name__ == "__main__":
    main()
