import sys

sys.path.append("./.")

from math import lgamma
from numba import jit
import numpy as np

import numpy as np
from scipy.special import beta as B
from scipy.stats import beta

from src.utils.decorators import print_execution_time


@print_execution_time
def h(a, b, c, d):

    y = 1

    for j in range(c):

        temp = y

        y = y - B(a + j, b + d) / ((d + j) * B(1 + j, d) * B(a, b))

        if np.isnan(y):
            y = temp
            break

    return y


@print_execution_time
def beta_loss_exact(beta1, beta2) -> float:

    if beta1.mean() > beta2.mean():
        t = beta1
        beta1 = beta2
        beta2 = t

    a, b = beta1.args
    c, d = beta2.args

    loss_exp = B(a + 1, b) * h(a + 1, b, c, d) / B(a, b) - B(c + 1, d) * h(
        a, b, c + 1, d
    ) / B(c, d)

    return loss_exp


@print_execution_time
def beta_loss_numeric(beta1, beta2, num_of_nodes: int = 500):
    h = 1 / (num_of_nodes - 1)

    if beta1.mean() > beta2.mean():
        t = beta1
        beta1 = beta2
        beta2 = t

    # now we have beta2 > beta1

    loss_exp = 0

    for i in range(num_of_nodes):
        for j in range(i):
            x, y = (i * h, j * h)
            loss_exp = loss_exp + beta1.pdf(x) * beta2.pdf(y) * (x - y) * h**2

    return loss_exp


# defining the functions used
@jit
def h(a, b, c, d):
    num = lgamma(a + c) + lgamma(b + d) + lgamma(a + b) + lgamma(c + d)
    den = lgamma(a) + lgamma(b) + lgamma(c) + lgamma(d) + lgamma(a + b + c + d)
    return np.exp(num - den)


@jit
def g0(a, b, c):
    return np.exp(lgamma(a + b) + lgamma(a + c) - (lgamma(a + b + c) + lgamma(a)))


@jit
def hiter(a, b, c, d):
    while d > 1:
        d -= 1
        yield h(a, b, c, d) / d


def g(a, b, c, d):
    return g0(a, b, c) + sum(hiter(a, b, c, d))


def calc_prob_between(beta1, beta2):
    return g(beta1.args[0], beta1.args[1], beta2.args[0], beta2.args[1])


def main():

    beta1 = beta(100, 303)
    beta2 = beta(203, 707)
    print(beta_loss_exact(beta1, beta2))
    print(beta_loss_numeric(beta1, beta2))
    print(calc_prob_between(beta1, beta2))


if __name__ == "__main__":
    main()
