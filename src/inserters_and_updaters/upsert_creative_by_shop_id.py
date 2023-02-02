import sys

sys.path.append("././.")

from sqlalchemy import create_engine
import nltk
import json
import pangres
import numpy
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime, date
from time import sleep
from loguru import logger
import uuid

load_dotenv()

from src.database.pingers import *
from src.feature_extractors import *
from src.utils.help_functions import nan_to_none, read_csv_and_eval
from src.utils.decorators import print_execution_time
from src.database.pingers import *

from src.database.session import engine


from psycopg2.extensions import register_adapter, AsIs


def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)


def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)


@print_execution_time
def upsert_creative_by_shop_id(
    shop_id: int,
    session=SessionLocal(),
    creative_update_csv_path: str = "data/creative_update_metadata.csv",
    end_date: str = date.today().strftime("%Y-%m-%d"),
    update_df: pd.DataFrame = None,
) -> pd.DataFrame:

    register_adapter(numpy.float64, addapt_numpy_float64)
    register_adapter(numpy.int64, addapt_numpy_int64)

    first_update_success = True
    second_update_success = True

    shop_id = str(shop_id)

    text_features = [
        "primary",
        "title",
        "description",
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
        "emojis",
    ]

    other_features = [
        "creative_type",
        "target",
        "targets_US",
        "targets_english",
        "number_of_countries",
        "number_of_custom_audiences",
        "age_range",
    ]

    features = text_features + other_features

    if update_df is None:
        update_df = read_csv_and_eval(creative_update_csv_path).set_index(["shop_id"])

    if shop_id not in update_df.index:
        update_df.loc[shop_id] = {"features": [], "last_updated": "2015-01-01"}

    old_features = update_df.loc[shop_id, "features"]

    new_features = list(set(features) - set(old_features))

    end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")

    last_updated = update_df.loc[shop_id, "last_updated"]
    logger.debug(f"last_updated: {last_updated}")
    last_updated_dt = datetime.strptime(last_updated, "%Y-%m-%d")

    if len(new_features) == 0 and last_updated_dt >= end_date_dt:
        return update_df, True

    df = ping_raw_creative_and_target(shop_id=shop_id)

    logger.debug(f"df: {df}")

    if len(new_features):

        df = df.apply(extract_text_and_type, axis=1)

        if len(set(new_features).intersection(set(text_features))):
            # print("applying text features...")
            df = get_all_text_features(df)
            # print("finished.")

        df = get_target_features(df)

        first_update_success = upsert_columns(df, new_features)

    # we don't need ads before start_date anymore so...

    if end_date_dt > last_updated_dt and len(df) > 0 and last_updated != "2015-01-01":

        new_ad_ids_query = query_ad_id(
            session=session, start_date=last_updated, shop_id=shop_id
        )
        new_ad_ids = pd.read_sql(new_ad_ids_query.statement, session.bind)["ad_id"]

        df = df.loc[df.ad_id.isin(new_ad_ids), :]

        if "primary" not in df.columns:
            df = df.apply(extract_text_and_type, axis=1)

        if "targets_US" not in df.columns:
            df = get_target_features(df)

        print(f"novih adova ima {df.ad_id.nunique()}.")

        if (
            len(set(old_features).intersection(set(text_features)))
            and "emojis" not in df.columns
        ):
            # print("applying text features...")
            df = df = get_all_text_features(df)
            # print("finished.")

        second_update_success = upsert_columns(df, old_features)

    # registering an update
    if first_update_success and second_update_success:
        update_df.loc[shop_id, "last_updated"] = end_date
        update_df.loc[shop_id, "features"].extend(new_features)
        success = True
    else:
        success = False

    return update_df, success


def upsert_columns(df: pd.DataFrame, features: list[str]):

    # print(df.columns)
    print(f"features: {features}")

    if not len(features) or not len(df):
        return True

    key_columns = ["ad_id", "shop_id", "account_id", "creative_id"]

    db_columns = key_columns + features

    df = df.loc[:, db_columns]

    shop_id = df.shop_id.unique()[0]

    # print(f"jedinstvenost: {df.ad_id.nunique()/len(df)}")

    df.set_index(key_columns, inplace=True)

    db_table = (
        pd.DataFrame(df.stack(dropna=False))
        .reset_index()
        .rename(columns={"level_4": "feature", 0: "value"})
    )

    # db_table.to_csv(f"data/test/{shop_id}_{str(uuid.uuid4())}.csv", index=False)

    db_table["value"] = db_table.value.apply(json.dumps)

    logger.debug(db_table)

    # print(db_table[db_table.feature.isin(text_columns)])

    db_table.set_index(["ad_id", "account_id", "shop_id", "feature"], inplace=True)

    conn = engine.connect()

    print("inserting...")
    i = 0
    while i < 5:
        try:
            pangres.upsert(
                con=conn,
                df=db_table,
                table_name="ad_creative_features",
                if_row_exists="update",
                create_table=False,
                chunksize=len(features) * 4,
            )
            break
        except:
            print(f"i: {i}")
            i = i + 1
            sleep(10)

    print("finished inserting.")

    if i == 5:
        return False

    return True


def main():
    print("hola")
    update_df = read_csv_and_eval(path="data/creative_update_metadata.csv")
    update_df.set_index("shop_id", inplace=True)

    update_df, success = upsert_creative_by_shop_id(
        shop_id=26660035, update_df=update_df
    )

    logger.debug(f"success: {success}")
    # print(update_df.loc["16038", :])

    # if success:
    #     update_df.to_csv("./././data/creative_update_metadata.csv")
    # print(f"success: {success}")


if __name__ == "__main__":
    main()
