import sys

sys.path.append("././.")
import inspect

import numpy as np
import pandas as pd
from scipy.stats import f, f_oneway

from src.pingers import *
from src.statistical_tests.get_binomial_sample import get_binomial_sample
from src.utils import *


def _f_oneway(*args, **kwargs):
    result = f_oneway(*args, **kwargs)
    return result


def get_sample_var_sum(positive: int, size: int, mean: float):
    result = (1 - 2 * mean) * positive + size * mean**2
    return result


def f_oneway_bernoulli(positives: pd.Series | list, sizes: pd.Series | list):
    if len(positives) != len(sizes):
        exit(
            f"{sys.argv[0]}/{inspect.stack()[0][3]} LengthError: Lengths of positives and sizes in ANOVA must be the same!"
        )

    k = len(positives)
    n = np.sum(sizes)

    # print(f"k: {k}")
    # print(f"n: {n}")

    means = [positive / size for positive, size in zip(positives, sizes)]
    global_mean = np.sum(positives) / np.sum(sizes)

    # calculating mst
    sst = np.sum([size * (mean - global_mean) ** 2 for size, mean in zip(sizes, means)])
    mst = sst / (k - 1)

    # print(f"mst: {mst}")

    # calculating mse
    var_sums = [
        get_sample_var_sum(positive=positive, size=size, mean=mean)
        for positive, size, mean in zip(positives, sizes, means)
    ]
    sse = sum(var_sums)
    mse = sse / (n - k)
    # print(f"mse: {mse}")

    f_stat = mst / mse

    p_value = f.sf(x=f_stat, dfn=k - 1, dfd=n - k)

    return f_stat, p_value


def main():
    df = ping_facebook_creative_and_performance(shop_id="2")
    samples = [get_binomial_sample(positive=positive, size=size) for positive, size in zip(positives, sizes)]
    f_moj, p_moj = f_oneway_bernoulli(positives=positives, sizes=sizes)
    print(f"moji: {[f_moj, p_moj]}")
    f, p = _f_oneway(*samples)
    print(f"pravi: {[f, p]}")


if __name__ == "__main__":
    main()
