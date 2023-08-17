FRONTEND_NAMES_DICT = {
    "impr": "impressions",
    "n_ads": "number of ads",
    "n_shops": "number of shops",
    "purch": "purchases",
    "purch_value_USD": "purchase value",
    "spend_USD": "ad spend",
}


def get_frontend_name(backend_name: str) -> str:
    return FRONTEND_NAMES_DICT.get(backend_name, backend_name.replace("_", " "))
