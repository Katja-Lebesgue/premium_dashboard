features = [
    "emojis",
    "urgency",
    "percentages",
    "prices",
    "cta",
    "fact_words",
    "discounts",
    "prices",
    "links",
    "user_addressing",
    "hashtags",
    "free_shipping",
    "length",
    "starts_with_question",
]

boolean_text_features = [
    "emojis_any",
    "urgency_any",
    "percentages_any",
    "prices_any",
    "cta_any",
    "fact_words_any",
    "discounts_any",
    "starts_with_question_any",
    "links_any",
    "user_addressing_any",
    "hashtags_any",
    "free_shipping_any",
]

text_features = boolean_text_features + ["emojis"]

other_features = [
    "creative_type",
    "target",
    "targets_US",
    "targets_english",
    "number_of_countries",
    "number_of_custom_audiences",
    "age_range",
]


column_dtypes = {"shop_id": str, "account_id": str, "ad_id": str, "creative_id": str}


text_columns = ["primary", "title", "description"]

tests = ["fisher_exact_test", "mean_test", "proportion_test"]
metrics = ["ctr", "cr"]
