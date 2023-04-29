import time
from datetime import timedelta


def print_execution_time(func):
    def wrapper_time(*args, **kwargs):
        start = time.perf_counter()
        a = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__}: {str(timedelta(seconds=end - start))}")
        return a

    return wrapper_time
