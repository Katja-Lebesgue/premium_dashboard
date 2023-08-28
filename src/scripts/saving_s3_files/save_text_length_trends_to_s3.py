import sys

sys.path.append("././.")

import warnings

import numpy as np
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session
from tqdm import tqdm

from metadata.globals import *
from src.pingers import *
from src.utils import *

warnings.filterwarnings("ignore", message="Mean of empty slice")
warnings.filterwarnings("ignore", message="invalid value encountered in double_scalars")
warnings.filterwarnings(
    "ignore",
    message="The values in the array are unorderable. Pass `sort=False` to suppress this warning.",
)


@print_execution_time
def save_text_length_trends_to_s3(
    db: Session,
    folder=f"prljavo/",
    bucket="creative-features",
    csv_file_name: str = None,
    end_date=date.today().strftime("%Y-%m-%d"),
    force_from_scratch: bool = False,
):
    if csv_file_name is None:
        csv_file_name = f"text_length_{end_date}"

    table_path = folder + csv_file_name + ".csv"

    done_shop_ids_path = folder + csv_file_name + "_done_shop_ids" + ".csv"

    logger.debug("pinging shops...")
    shop_ids_query = db.query(AdCreativeFeatures.shop_id).distinct()
    all_shop_ids = pd.read_sql(shop_ids_query.statement, db.bind)["shop_id"]
    logger.debug("done!")

    group_cols = [
        "year_month",
    ]

    list_of_objects = list_objects_from_prefix(prefix=table_path)
    from_scratch = len(list_of_objects) == 0 or force_from_scratch

    # table was already created today
    if not from_scratch:
        table = read_csv_from_s3(path=table_path)
        table.set_index(keys=group_cols, inplace=True)

        done_shop_ids = read_csv_from_s3(path=done_shop_ids_path, bucket=bucket)["shop_id"]

        logger.debug(f"we have {len(done_shop_ids)} done shop ids.")

        shop_ids = all_shop_ids[~all_shop_ids.isin(done_shop_ids)]

    else:
        table = pd.DataFrame()
        shop_ids = all_shop_ids

    loader = tqdm(enumerate(shop_ids), total=len(shop_ids))

    for shop_iter, shop_id in loader:
        loader.set_postfix({"shop_id": str(shop_id)})

        if shop_iter % 10 == 5:
            save_csv_to_s3(
                df=table,
                path=table_path,
                bucket=bucket,
            )
            done_shop_ids = all_shop_ids
            done_shop_ids_df = pd.DataFrame(done_shop_ids, columns=["shop_id"])
            save_csv_to_s3(df=done_shop_ids_df, bucket=bucket, path=done_shop_ids_path)

        try:
            new = get_new_table_by_shop_id(db=db, shop_id=shop_id)

            if shop_iter == 0 and from_scratch:
                table = new
            else:
                table = table.add(new, fill_value=0)

        except Exception:
            logger.exception(f"shop_id = {shop_id}")
            new = pd.DataFrame()

        # logger.debug(table)

        # if shop_iter == 5:
        #     return table

    save_csv_to_s3(
        df=table,
        path=table_path,
        bucket=bucket,
    )

    done_shop_ids = all_shop_ids
    done_shop_ids_df = pd.DataFrame(done_shop_ids, columns=["shop_id"])
    save_csv_to_s3(df=done_shop_ids_df, bucket=bucket, path=done_shop_ids_path)

    return table


def f(df):
    result = {}
    for text in set(df.columns).intersection({"primary", "title", "description"}):
        filtered = df[df[text].apply(len) > 0]
        result[f"{text}_num_shops"] = int(filtered.spend.sum() > 0)
        if result[f"{text}_num_shops"]:
            length_mean = np.average(filtered[text].apply(lambda x: len(x[0])), weights=filtered.spend)
            result[f"{text}_length"] = length_mean
    return result


def get_new_table_by_shop_id(db: Session, shop_id: int) -> pd.DataFrame:
    df = ping_facebook_creative_and_performance(db=db, shop_id=shop_id)

    if any([x not in df.columns for x in ["primary", "year_month"]]):
        return pd.DataFrame()

    df = df[df.primary.notna()]
    df = df[df.primary.apply(len) > 0]
    return df.groupby("year_month").apply(f).apply(pd.Series)
