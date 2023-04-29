import numpy as np
from scipy.stats import f

from src.statistical_tests import *


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
