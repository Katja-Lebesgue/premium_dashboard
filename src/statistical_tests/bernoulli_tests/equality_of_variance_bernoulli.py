import pandas as pd
from scipy.stats import chi2_contingency


def get_sample_var(positive: int, size: int, mean: float):
    result = (1 - 2 * mean) * positive + size * mean**2
    result = result / (size - 1)
    return result


def equality_of_variance_bernoulli(positives: list, sizes: list) -> float:
    negatives = [size - positive for size, positive in zip(sizes, positives)]
    table = pd.DataFrame([positives, negatives])
    table = table.T
    chi2_stat, p, a, b = chi2_contingency(table)
    return chi2_stat, p
