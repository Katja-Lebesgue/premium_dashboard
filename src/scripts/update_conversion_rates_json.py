import sys

sys.path.append("./.")

import requests
import os
from dotenv import load_dotenv

from src.s3 import *

load_dotenv()


def update_conversion_rates_json(
    path: str = "conversion_rates.txt", bucket: str = "creative-features"
):

    url = f'https://v6.exchangerate-api.com/v6/{os.getenv("EXCHANGERATE_APIKEY")}/latest/USD'

    response = requests.get(url)
    data = response.json()

    conversion_rates = data["conversion_rates"]

    save_json_to_s3(d=conversion_rates, path=path, bucket=bucket)

    return


if __name__ == "__main__":
    update_conversion_rates_json()
