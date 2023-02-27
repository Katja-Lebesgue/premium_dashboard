import sys

sys.path.append("./.")

import pandas as pd

metric_dict = {
    "spend_USD": "spend",
    "impr": "impressions",
    "link_clicks": "link clicks",
    "purch": "purchases",
}

metric_dict_shop = metric_dict | {"count": "ads"}


metric_dict_market = metric_dict | {
    "count_ads": "ads",
    "count_shops": "shops",
}


pie_groups_dict = {
    "discounts_any": "promotion",
    "promotion": "promotion",
    "creative_type": "creative type",
    "target": "target",
}

google_pie_groups_dict = {"type": "type"}

custom_feature_dict = {
    "urgency_any": "urgency",
    "discounts_any": "promotion",
    "prices_any": "price",
    "emojis_any": "contains emojis",
    "fact_words_any": "mentions facts",
    "user_addressing_any": "adresses user",
    "starts_with_question_any": "starts with question",
}


feature_dict = custom_feature_dict | {
    "creative_type": "creative type",
}

targeting_dict = {
    "targets_US": "US",
    "targets_english": "English countries",
    "all": "all",
}

custom_group_dict = {"target": "target", "creative_type": "creative type"}

feature_dict_market = {
    "emojis": "contains emojis",
    "urgency": "urgency",
    "question": "question",
    "you": "adresses user",
    "facts": "mentions facts",
    "price": "price",
}
