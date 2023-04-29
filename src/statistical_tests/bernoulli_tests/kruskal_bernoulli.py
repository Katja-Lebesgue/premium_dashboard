from scipy.stats import chi2, kruskal

from src.statistical_tests import *


def kruskal_bernoulli(positives: list, sizes: list) -> float:
    negatives = [size - positive for size, positive in zip(sizes, positives)]
    means = [positive / size for positive, size in zip(positives, sizes)]

    N = sum(sizes)
    k = len(sizes)

    global_positive = sum(positives)
    global_negative = sum(negatives)

    rank_0 = (global_negative + 1) / 2
    rank_1 = global_negative + (global_positive + 1) / 2

    rs = [
        get_r(positive=positive, negative=negative, rank_0=rank_0, rank_1=rank_1)
        for positive, negative in zip(positives, negatives)
    ]

    global_r = (N + 1) / 2

    denominator = sum(
        [
            positive * (rank_1 - global_r) ** 2 + negative * (rank_0 - global_r) ** 2
            for positive, negative in zip(positives, negatives)
        ]
    )

    fraction = sum([size * (r - global_r) ** 2 / denominator for size, r in zip(sizes, rs)])

    H = (N - 1) * fraction

    p_value = chi2.sf(x=H, df=k - 1)

    return H, p_value


def get_r(positive: int, negative: int, rank_0: int, rank_1: int):
    r = positive * rank_1 + negative * rank_0
    r = r / (positive + negative)
    return r
