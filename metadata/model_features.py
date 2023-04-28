import sys

sys.path.append(".")

from metadata.globals import features

bool_features = [feature + "_any" for feature in features if feature != "length"]

categorical_features = ["creative_type", "industry", "target"]

numerical_features = [
    "aov",
    "number_of_countries",
    "number_of_custom_audiences",
    "age_range",
]


performance_columns = ["cr", "ctr", "impr", "link_clicks", "purch", "spend"]

model_features = bool_features + categorical_features + numerical_features


fillna_dict = {
    "shop_id": "unknown",
    "account_id": "unknown",
    "ad_id": "unknown",
}
