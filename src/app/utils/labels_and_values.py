import sys

sys.path.append("./.")

from src.database.myDB import DBConnect
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


def get_shop_dict():

    cursor = DBConnect()

    query = f"""
    select id, name
    from shop
        """

    cursor.execute(query)

    data = cursor.fetchall()
    cols = []

    for elt in cursor.description:
        cols.append(elt[0])

    df = pd.DataFrame(data=data, columns=cols).astype(str)

    shop_dict = dict(zip(df.id, df.name))

    return shop_dict


shop_dict = get_shop_dict()


def main():
    print(get_shop_dict().keys())


if __name__ == "__main__":
    main()
