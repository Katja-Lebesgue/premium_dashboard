from typing import Any

from src.utils.enum import convert_enum_to_its_value

FRONTEND_NAMES_DICT = {
    "impr": "impressions",
    "n_ads": "number of ads",
    "n_shops": "number of shops",
    "purch": "purchases",
    "purch_value_USD": "purchase value",
    "spend_USD": "ad spend",
    "acquisition": "prospecting",
    "remarketing": "retargeting",
}


def get_frontend_name(backend_name: Any) -> str:
    backend_name = convert_enum_to_its_value(backend_name)
    return FRONTEND_NAMES_DICT.get(str(backend_name), str(backend_name).replace("_", " "))
