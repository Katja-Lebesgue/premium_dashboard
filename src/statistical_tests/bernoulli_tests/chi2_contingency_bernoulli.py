import pandas as pd
from scipy.stats import chi2_contingency


def chi2_contingency_bernoulli(positives: list, sizes: list) -> float:
    negatives = [size - positive for size, positive in zip(sizes, positives)]
    table = pd.DataFrame([positives, negatives])
    table = table.T
    chi2_stat, p, a, b = chi2_contingency(table)
    return chi2_stat, p
