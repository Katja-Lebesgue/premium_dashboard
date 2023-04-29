def get_binomial_sample(positive: int, size: int = None, negative: int = None):
    sample = [1] * positive
    if negative is None:
        negative = size - positive
    sample = sample + [0] * negative
    return sample
