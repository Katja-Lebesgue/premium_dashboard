import sys

sys.path.append("././.")

import warnings

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from tqdm import tqdm

from src.pingers import *
from src.statistical_tests import *
from src.utils import *

warnings.filterwarnings("ignore", message="Mean of empty slice")
warnings.filterwarnings("ignore", message="invalid value encountered in double_scalars")


@print_execution_time
def save_global_promotion_tests_to_s3(
    db: Session,
    start_date: str = "2015-01-01",
    end_date: str = datetime.strftime(datetime.today(), "%Y-%m-%d"),
    folder="prljavo/",
    bucket="creative-features",
    csv_file_name: str = None,
    force_from_scratch: bool = False,
):
    if csv_file_name is None:
        csv_file_name = f"global_promotion_tests_from_{start_date}_to_{end_date}"

    done_shop_ids_csv_name = csv_file_name + "_done_shop_ids"

    table_path = folder + csv_file_name + ".csv"

    done_shop_ids_path = folder + done_shop_ids_csv_name + ".csv"

    # shop_ids_query = db.query(AdCreativeFeatures.shop_id).distinct()
    shop_ids_query = db.query(Shop.id).distinct()
    all_shop_ids = read_query_into_df(db=db, query=shop_ids_query)["shop_id"]

    idx_cols = [
        "shop_id",
        "target",
    ]

    table_columns = ["proportion_test_ctr", "proportion_test_cr"]

    list_of_objects = list_objects_from_prefix(prefix=table_path)

    from_scratch = len(list_of_objects) == 0 or force_from_scratch

    if not from_scratch:
        table = read_csv_from_s3(path=table_path)
        done_shop_ids = read_csv_from_s3(path=done_shop_ids_path, bucket=bucket)["shop_id"].astype(int)
        logger.debug(f"total of {len(all_shop_ids)} shop ids.")
        logger.debug(f"we have {len(done_shop_ids)} done shop ids.")
        shop_ids = all_shop_ids[~all_shop_ids.isin(done_shop_ids)]
        logger.debug(f"{len(shop_ids)} more to go")

    else:
        table = pd.DataFrame(columns=idx_cols + table_columns)

        shop_ids = all_shop_ids

    for shop_iter, shop_id in tqdm(enumerate(shop_ids), total=len(shop_ids)):
        logger.debug(f"shop_id: {shop_id}")

        if shop_iter % 10 == 5:
            save_csv_to_s3(
                df=table,
                path=table_path,
                bucket=bucket,
            )

            done_shop_ids = shop_ids[: shop_iter - 1]
            done_shop_ids_df = pd.DataFrame(done_shop_ids, columns=["shop_id"])

            save_csv_to_s3(df=done_shop_ids_df, bucket=bucket, path=done_shop_ids_path)

        data_shop = ping_facebook_creative_and_performance(
            db=db, shop_id=shop_id, start_date=start_date, end_date=end_date
        )

        if len(data_shop) == 0 or any(
            [x not in data_shop.columns for x in ["spend_USD", "discounts_any", "targets_US"]]
        ):
            continue

        data_shop = data_shop.loc[data_shop.targets_US == True, :]
        data_shop = data_shop[
            (data_shop.link_clicks >= data_shop.purch) & (data_shop.impr >= data_shop.link_clicks)
        ]

        for target in ["acquisition", "remarketing"]:
            data_shop_target = data_shop.loc[data_shop.target == target]

            if len(data_shop_target) == 0:
                continue

            group_true = data_shop_target.loc[data_shop_target.discounts_any == True, :]
            group_false = data_shop_target.loc[data_shop_target.discounts_any == False, :]

            new_idx = {"shop_id": shop_id, "target": target}
            new_columns = {
                "proportion_test_ctr": proportion_test_ctr(
                    group1=group_true, group2=group_false, convert_nan_to_none=True
                ),
                "proportion_test_cr": proportion_test_cr(
                    group1=group_true, group2=group_false, convert_nan_to_none=True
                ),
            }

            new_row = new_idx | new_columns

            table.loc[len(table), :] = new_row

    save_csv_to_s3(
        df=table,
        path=table_path,
        bucket=bucket,
    )

    done_shop_ids = all_shop_ids
    done_shop_ids_df = pd.DataFrame(done_shop_ids, columns=["shop_id"])

    save_csv_to_s3(df=done_shop_ids_df, bucket=bucket, path=done_shop_ids_path)


def main():
    save_global_promotion_tests_to_s3(start_date="2021-06-03")


if __name__ == "__main__":
    main()
