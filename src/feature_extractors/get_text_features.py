import sys

sys.path.append("./.")


import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from multiset import *
from src.database.session import *
from src.database.queries import *

from src.utils.decorators import print_execution_time
from src.feature_extractors.text_analysis_functions import *
from src.feature_extractors.extract_text_and_type import *


from metadata.globals import *

from metadata.nltk_stuff import sia


text_columns = ["primary", "title", "description"]

feature_func_dict = {
    "emojis": get_emojis,
    "urgency": has_urgency,
    "percentages": get_percentages,
    "prices": get_prices,
    "cta": has_cta,
    "fact_words": get_fact_words,
    "discounts": get_discounts,
    "starts_with_question": starts_with_question,
    "prices": get_prices,
    "links": get_links,
    "user_addressing": get_user_addressing,
    "hashtags": get_hashtags,
    "free_shipping": has_free_shipping,
    "length": len,
}


@print_execution_time
def get_all_text_features(
    df: pd.DataFrame, get_sentiment: bool = False
) -> pd.DataFrame:

    if len(df) == 0:
        return df

    for text_col in text_columns:
        for feature, func in feature_func_dict.items():
            df = get_text_feature_for_all(
                df=df, feature=feature, text_col=text_col, func=func
            )

    df.prices_any = df.apply(lambda df: df.prices_any | df.has_dynamic_price, axis=1)

    feature = "percentages_that_are_not_promotions"
    for text_col in text_columns:

        df[f"{text_col}_{feature}_any"] = df.apply(
            lambda df: has_any(
                [
                    multiset_difference(a, b)
                    for b, a in zip(
                        [
                            [get_percentages(x)[0] for x in discounts]
                            for discounts in df[f"{text_col}_discounts"]
                        ],
                        df[f"{text_col}_percentages"],
                    )
                ]
            ),
            axis=1,
        )

    df = get_global_boolean_text_feature(df=df, feature=feature)

    df.fact_words_any = df.apply(
        lambda df: df[f"{feature}_any"] | df.fact_words_any, axis=1
    )

    if get_sentiment:
        df = get_sentiment_for_all(df)

    return df


def get_sentiment_for_all(df: pd.DataFrame):

    for text_col in text_columns:
        df = get_sentiment(df=df, col=text_col)

    for method in ["nltk", "textblob"]:

        df[f"polarity_{method}"] = df.apply(
            lambda df: get_average_polarity_scores(
                sum(
                    [df[f"{text_col}_polarity_{method}"] for text_col in text_columns],
                    [],
                )
            ),
            axis=1,
        )

    return df


def get_sentiment(df: pd.DataFrame, col: str):

    # print(df[col])

    df[f"{col}_polarity_textblob"] = df[col].apply(
        lambda texts: [TextBlob(text).polarity for text in texts]
    )

    df[f"{col}_polarity_nltk"] = df[col].apply(
        lambda texts: [sia.polarity_scores(text) for text in texts]
    )

    for method in ["textblob", "nltk"]:
        df[f"{col}_polarity_{method}_mean"] = df[f"{col}_polarity_{method}"].apply(
            get_average_polarity_scores
        )

    return df


def get_text_feature_for_all(
    df: pd.DataFrame,
    feature: str,
    text_col: str,
    func,
):
    for text_col in text_columns:
        df = get_text_feature(
            df=df, feature=feature, text_col=text_col, func=func, add_any_col=True
        )
    df = get_global_boolean_text_feature(df=df, feature=feature)

    if feature == "emojis":

        df[feature] = df.apply(
            lambda df: list_of_lists_to_list(
                [df[f"{text_col}_emojis"] for text_col in text_columns]
            ),
            axis=1,
        )

    return df


def list_of_lists_to_list(l: list) -> list:
    result = []

    for i in l:
        for j in i:
            result.extend(j)

    return result


def get_global_boolean_text_feature(df: pd.DataFrame, feature: str):

    df[f"{feature}_any"] = df.apply(
        lambda df: any([df[f"{text_col}_{feature}_any"] for text_col in text_columns]),
        axis=1,
    )

    return df


def get_text_feature(
    df: pd.DataFrame,
    feature: str,
    text_col: str,
    func,
    add_any_col: bool = False,
):

    df[f"{text_col}_{feature}"] = df[text_col].apply(
        lambda texts: [func(text) for text in texts]
    )

    if add_any_col:
        df[f"{text_col}_{feature}_any"] = df[f"{text_col}_{feature}"].apply(has_any)

    return df


def get_average_polarity_scores(polarity_scores: list[dict]) -> dict:

    if not len(polarity_scores):
        return None

    if type(polarity_scores[0]) == dict:

        criteria = ["pos", "neg", "neu", "compound"]

        result = dict()
        for key in criteria:
            result[key] = np.mean([scores[key] for scores in polarity_scores])

    else:
        result = np.mean(polarity_scores)

    return result


def has_any(l: list):

    if not len(l):
        return None

    if type(l[0]) == dict:
        return has_any_keywords(l)

    if type(l[0]) == list:
        return list_of_lists_is_not_empty(l)

    if type(l[0]) in [bool, int]:
        return any(l)

    return None


def list_of_lists_is_not_empty(l: list) -> bool:

    if not len(l):
        return None

    return bool(sum([len(item) for item in l]))


def has_any_keywords(l: list[dict]) -> bool:
    return bool(sum([sum(d.values()) for d in l]))


def multiset_difference(a, b):

    result = (
        list(Multiset(a).difference(Multiset(b)))
        if Multiset(a).difference(Multiset(b))
        else []
    )

    return result


def main():
    session = SessionLocal()
    query = query_raw_creative_data(shop_id=2)
    df = pd.read_sql(query.statement, session.bind)
    df = df.apply(extract_text_and_type, axis=1)
    df = get_all_text_features_proba(df=df)
    return


if __name__ == "__main__":
    main()
