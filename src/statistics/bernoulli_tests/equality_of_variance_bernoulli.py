import sys

sys.path.append("././.")

from numpy import size
from scipy.stats import fisher_exact
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

from src.utils.common import nan_to_none
from src.utils.decorators import print_execution_time


def get_sample_var(positive: int, size: int, mean: float):
    result = (1 - 2 * mean) * positive + size * mean**2
    result = result / (size - 1)
    return result


def equality_of_variance_bernoulli(positives: list, sizes: list) -> float:

    negatives = [size - positive for size, positive in zip(sizes, positives)]

    table = pd.DataFrame([positives, negatives])

    table = table.T

    print(table)

    chi2_stat, p, a, b = chi2_contingency(table)

    return chi2_stat, p


def main():
    positives = [100, 120, 20]
    sizes = [1000, 1270, 60]
    f_moj, p_moj = chi2_contingency_bernoulli(positives=positives, sizes=sizes)
    print(f"moji: {[f_moj, p_moj]}")


if __name__ == "__main__":
    main()
