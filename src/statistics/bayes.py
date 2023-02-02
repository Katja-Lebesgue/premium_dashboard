import sys

sys.path.append("./.")

import pandas as pd
from src.statistics.beta_statistics import *
from scipy.stats import beta

from src.utils.decorators import print_execution_time


def prior_to_posterior(beta_var, n: int, c: int) -> beta:
    a, b = beta_var.args
    return beta(a + c, b + n - c)


@print_execution_time
def bayes_step(beta_A, beta_B, n_A, c_A, n_B, c_B):

    beta_A = prior_to_posterior(beta_A, n_A, c_A)
    beta_B = prior_to_posterior(beta_B, n_B, c_B)

    loss = beta_loss_numeric(beta_A, beta_B)

    return beta_A, beta_B, loss


@print_execution_time
def bayes_test(
    sample_A: pd.DataFrame,
    sample_B: pd.DataFrame,
    n_col: str,
    c_col: str,
    epsilon: float = None,
):

    if epsilon is None:

        mean_A = sample_A[c_col].sum() / sample_A[n_col].sum()
        mean_B = sample_B[c_col].sum() / sample_B[n_col].sum()

        epsilon = 0.1 * min(mean_A, mean_B)

    sample_A = (
        sample_A[sample_A[n_col] > 0].sort_values(n_col, ascending=False).reset_index()
    )
    sample_B = (
        sample_B[sample_B[n_col] > 0].sort_values(n_col, ascending=False).reset_index()
    )

    len_A = len(sample_A)
    len_B = len(sample_B)

    print(f"{len_A}, {len_B}")

    if len_A == 0 or len_B == 0:
        return None

    max_len = max(len_A, len_B)

    beta_A = beta(1, 1)
    beta_B = beta(1, 1)

    i = 0

    while True:

        n_A = sample_A.loc[i % max_len, n_col]
        c_A = sample_A.loc[i % max_len, c_col]
        n_B = sample_B.loc[i % max_len, n_col]
        c_B = sample_B.loc[i % max_len, c_col]

        beta_A, beta_B, loss = bayes_step(
            beta_A=beta_A, beta_B=beta_B, n_A=n_A, c_A=c_A, n_B=n_B, c_B=c_B
        )

        print(f"beta_A: beta{(beta_A.args)}")
        print(f"beta_B: beta{(beta_B.args)}")
        print(f"loss: {loss}")

        if loss < epsilon:
            if beta_A.mean() > beta_B.mean():
                winner = "A"
            else:
                winner = "B"
            print("konj")
            break

        i = i + 1

    return winner
