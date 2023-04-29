from itertools import combinations


def get_all_subsets(s: set | list):
    n = len(s)
    subsets = []
    for i in range(n + 1):
        i_subsets = combinations(s, i)
        subsets.extend(i_subsets)
    return subsets


def add_two_dicts(d1: dict, d2: dict) -> dict:
    return {k: d1.get(k, 0) + d2.get(k, 0) for k in d1.keys() | d2.keys()}
