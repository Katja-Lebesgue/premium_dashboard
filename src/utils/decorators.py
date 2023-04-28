import inspect
import time
from datetime import timedelta


def print_start(func):
    def wrapper_print_start(*args, **kwargs):
        print(f"Started {func.__name__}...")
        return func(*args, **kwargs)

    return wrapper_print_start


def print_execution_time(func):
    def wrapper_time(*args, **kwargs):
        start = time.perf_counter()
        a = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__}: {str(timedelta(seconds=end - start))}")
        return a

    return wrapper_time


def probna(a):
    frame = inspect.currentframe()
    b = 5
    args, _, _, values = inspect.getargvalues(frame)
    print(f"{probna.__name__}{tuple(values)}")


if __name__ == "__main__":
    probna(3)
