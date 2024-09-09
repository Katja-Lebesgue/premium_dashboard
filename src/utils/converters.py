import math
import os

import bcrypt
import numpy as np
from dotenv import load_dotenv

load_dotenv()

salt = os.getenv("SALT").encode()


def hash_password(password: str):
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password


def separate_thousands_and_round(num: float | int | str, r: int = 2) -> str:
    if type(num) == str:
        num = float(num)
    num = round(num, r)
    return f"{num:,}".replace(",", " ")


def nan_to_none(num):
    if np.isnan(num) or math.isinf(num):
        return None
    else:
        return num


def big_number_human_format(num, big_decimals: int = 2, small_decimals: int = 0):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0

    if magnitude:
        num_format = f"%.{big_decimals}f%s" % (
            num,
            ["", "K", "M", "B", "T", "P"][magnitude],
        )
    else:
        num_format = f"%.{small_decimals}f%s" % (
            num,
            ["", "K", "M", "B", "T", "P"][magnitude],
        )

    return num_format


def convert_to_USD(price: float | int, currency: str, conversion_rates_dict: dict) -> float:
    if type(currency) != str or currency not in conversion_rates_dict.keys():
        return None
    return price / conversion_rates_dict[currency]


def element_to_list(a):
    if type(a) != list:
        a = [a]

    return list(a)


def none_to_unknown(a):
    if a is None or a == "None":
        return "unknown"
    return a
