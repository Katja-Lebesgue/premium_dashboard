import sys

sys.path.append("././.")

import warnings

import numpy as np
import pandas as pd
from pandas.core.common import SettingWithCopyWarning
from sqlalchemy.orm import Session
from tqdm import tqdm

from src.pingers import *
from src.statistical_tests import *
from src.statistical_tests.bernoulli_tests import *
from src.statistical_tests.proportion_test import proportion_test, proportion_test_cr, proportion_test_ctr
from src.utils import *

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

warnings.filterwarnings("ignore", message="Mean of empty slice")
warnings.filterwarnings("ignore", message="invalid value encountered in double_scalars")
warnings.filterwarnings("ignore", message="p-value may not be accurate for N > 5000.")
warnings.filterwarnings(
    "ignore",
    message="Input data for shapiro has range zero. The results may not be accurate.",
)


@print_execution_time
def save_global_creative_type_tests_to_s3(
    db: Session,
    start_date: str = "2015-01-01",
    end_date: str = datetime.strftime(datetime.today(), "%Y-%m-%d"),
    folder="prljavo/",
    bucket="creative-features",
    csv_file_name: str = None,
    force_from_scratch: bool = False,
):
    if csv_file_name is None:
        csv_file_name = f"global_creative_type_tests_from_{start_date}_to_{end_date}"

    done_shop_ids_csv_name = csv_file_name + "_done_shop_ids"

    table_path = folder + csv_file_name + ".csv"

    done_shop_ids_path = folder + done_shop_ids_csv_name + ".csv"

    # shop_ids_query = db.query(AdCreativeFeatures.shop_id).distinct()
    shop_ids_query = db.query(Shop.id).distinct()
    all_shop_ids = read_query_into_df(db=db, query=shop_ids_query)["shop_id"]

    idx_cols = ["shop_id", "target", "promotion"]

    table_columns = ["mean_test_ctr", "mean_test_cr"]

    list_of_objects = list_objects_from_prefix(prefix=table_path)

    from_scratch = len(list_of_objects) == 0 or force_from_scratch

    if not from_scratch:
        table = read_csv_from_s3(path=table_path)
        done_shop_ids = read_csv_from_s3(path=done_shop_ids_path, bucket=bucket)["shop_id"].astype(int)
        print(f"we have {len(done_shop_ids)} done shop ids.")
        shop_ids = all_shop_ids[~all_shop_ids.isin(done_shop_ids)]

    else:
        table = pd.DataFrame(columns=idx_cols + table_columns)
        shop_ids = all_shop_ids

    for shop_iter, shop_id in tqdm(enumerate(shop_ids), total=len(shop_ids)):
        print(f"shop_id: {shop_id}")

        data_shop = ping_facebook_creative_and_performance(
            db=db, shop_id=shop_id, start_date=start_date, end_date=end_date
        )

        if shop_iter % 10 == 5:
            save_csv_to_s3(
                df=table,
                path=table_path,
                bucket=bucket,
            )

            done_shop_ids = shop_ids[: shop_iter - 1]
            done_shop_ids_df = pd.DataFrame(done_shop_ids, columns=["shop_id"])

            save_csv_to_s3(df=done_shop_ids_df, bucket=bucket, path=done_shop_ids_path)

        if not len(data_shop) or any(
            [x not in data_shop.columns for x in ["impr", "creative_type", "targets_US"]]
        ):
            continue

        data_shop = data_shop.loc[data_shop.targets_US == True, :]

        data_shop = data_shop[
            (data_shop.link_clicks >= data_shop.purch) & (data_shop.impr >= data_shop.link_clicks)
        ]

        for promotion in [True, False]:
            data_shop_promotion = data_shop.loc[data_shop.discounts_any.isin([promotion]), :]

            for target in ["acquisition", "remarketing"]:
                data_shop_target = data_shop_promotion.loc[data_shop_promotion.target.isin([target]), :]

                result_ctr = mean_test_bernoulli_ctr(
                    df=data_shop_target,
                    group_col="creative_type",
                    convert_nan_to_none=True,
                )
                result_cr = mean_test_bernoulli_cr(
                    df=data_shop_target,
                    group_col="creative_type",
                    convert_nan_to_none=True,
                )

                new_index = {"shop_id": shop_id, "promotion": promotion, "target": target}
                new_columns = {"mean_test_ctr": result_ctr, "mean_test_cr": result_ctr}
                new_row = new_index | new_columns

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
    save_global_creative_type_tests_to_s3(start_date="2021-06-03")


if __name__ == "__main__":
    main()
