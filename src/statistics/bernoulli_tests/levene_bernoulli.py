import sys
from statistics import mean

sys.path.append("././.")

import numpy as np
import pandas as pd
from numpy import size
from scipy.stats import chi2_contingency, f, fisher_exact

from src.statistics import *
from src.utils.common import nan_to_none
from src.utils.decorators import print_execution_time


def get_median(positive: int, negative: int):
    if positive > negative:
        return 1
    elif positive < negative:
        return 0
    return 0.5


def get_z(positive: int, negative: int, mean: int):
    z = positive * (1 - mean) + negative * mean
    z = z / (positive + negative)
    return z


def levene_bernoulli(positives: list, sizes: list, use_medians: bool = True) -> float:

    negatives = [size - positive for size, positive in zip(sizes, positives)]

    if use_medians:
        means = [get_median(positive, negative) for positive, negative in zip(positives, negatives)]
    else:
        means = [positive / size for positive, size in zip(positives, sizes)]

    N = sum(sizes)
    k = len(sizes)

    zs = [
        get_z(positive=positive, negative=negative, mean=mean)
        for positive, negative, mean in zip(positives, negatives, means)
    ]

    global_z = np.sum([z * size for z, size in zip(zs, sizes)]) / N

    denominator = np.sum(
        [
            positive * (1 - mean - z) ** 2 + negative * (mean - z) ** 2
            for positive, mean, negative, z in zip(positives, means, negatives, zs)
        ]
    )

    fraction = np.sum([size * (z - global_z) ** 2 / denominator for size, z in zip(sizes, zs)])

    W = (N - k) * fraction / (k - 1)

    p_value = f.sf(x=W, dfn=k - 1, dfd=N - k)

    return W, p_value


def main():
    positives = [100, 120, 20]
    sizes = [1000, 1270, 60]
    samples = [get_binomial_sample(positive=positive, size=size) for positive, size in zip(positives, sizes)]

    f_moj, p_moj = levene_bernoulli(positives=positives, sizes=sizes)
    print(f"moji: {[f_moj, p_moj]}")
    f, p = levene(*samples)
    print(f"pravi: {[f, p]}")


if __name__ == "__main__":
    main()
