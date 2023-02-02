import sys

sys.path.append("././.")

import pandas as pd
import numpy as np

from src.statistics import *
from src.s3 import *
from src.database.pingers import *
from src.utils import *
from tqdm import tqdm
import warnings

from metadata.globals import *

warnings.filterwarnings("ignore", message="Mean of empty slice")
warnings.filterwarnings("ignore", message="invalid value encountered in double_scalars")


@print_execution_time
def save_global_feature_tests_to_s3(
    start_date: str = "2015-01-01",
    end_date: str = datetime.strftime(datetime.today(), "%Y-%m-%d"),
    folder="data/global/",
    bucket="creative-features",
    csv_file_name: str = None,
):

    if csv_file_name is None:
        csv_file_name = f"global_feature_tests_from_{start_date}_to_{end_date}"

    done_shop_ids_csv_name = csv_file_name + "_done_shop_ids"

    table_path = folder + csv_file_name + ".csv"

    done_shop_ids_path = folder + done_shop_ids_csv_name + ".csv"

    shops = ping_shops()
    all_shop_ids = shops["shop_id"]

    idx_cols = [
        "shop_id",
        "promotion",
        "target",
        "feature",
    ]

    table_columns = ["proportion_test_ctr", "proportion_test_cr"]

    list_of_objects = list_objects_from_prefix(prefix=table_path)

    # table was already created today
    if len(list_of_objects):
        # table was already created today

        table = read_csv_from_s3(path=table_path)
        table.set_index(keys=idx_cols, inplace=True)

        done_shop_ids = read_csv_from_s3(path=done_shop_ids_path, bucket=bucket)[
            "shop_id"
        ]

        print(f"we have {len(done_shop_ids)} done shop ids.")

        shop_ids = all_shop_ids[~all_shop_ids.isin(done_shop_ids)]

    else:
        idx = pd.MultiIndex.from_product(iterables=[[]] * len(idx_cols), names=idx_cols)
        table = pd.DataFrame(index=idx, columns=table_columns)

        shop_ids = all_shop_ids

    test_features = boolean_text_features
    print(test_features)

    if "discounts_any" in test_features:
        test_features.remove("discounts_any")

    for shop_iter, shop_id in tqdm(enumerate(shop_ids), total=len(shop_ids)):

        print(f"shop_id: {shop_id}")

        data_shop = ping_creative_and_performance(
            shop_id=shop_id, start_date=start_date, end_date=end_date, monthly=False
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

        if len(data_shop) == 0 or any(
            [
                x not in data_shop.columns
                for x in ["spend_USD", "discounts_any", "targets_US"]
            ]
        ):
            continue

        data_shop = data_shop.loc[data_shop.targets_US == True, :]
        data_shop = data_shop[
            (data_shop.link_clicks >= data_shop.purch)
            & (data_shop.impr >= data_shop.link_clicks)
        ]

        # print(data_shop)
        # print(f"columns: {data_shop.columns}")

        for promotion in [True, False]:
            data_shop_promotion = data_shop.loc[data_shop.discounts_any == promotion, :]

            for target in ["acquisition", "remarketing"]:
                data_shop_target = data_shop_promotion.loc[
                    data_shop_promotion.target == target, :
                ]

                for feature in test_features:

                    group_true = data_shop_target.loc[
                        data_shop_target[feature].isin([True]), :
                    ]
                    group_false = data_shop_target.loc[
                        data_shop_target[feature].isin([False]), :
                    ]

                    # print(f"group lengths: {len(group_true)}, {len(group_false)}")

                    new_row = {
                        "proportion_test_ctr": proportion_test_ctr(
                            group1=group_true,
                            group2=group_false,
                            convert_nan_to_none=True,
                        ),
                        "proportion_test_cr": proportion_test_cr(
                            group1=group_true,
                            group2=group_false,
                            convert_nan_to_none=True,
                        ),
                    }

                    table.loc[(shop_id, promotion, target, feature), :] = new_row

    save_csv_to_s3(
        df=table,
        path=table_path,
        bucket=bucket,
    )

    done_shop_ids = all_shop_ids
    done_shop_ids_df = pd.DataFrame(done_shop_ids, columns=["shop_id"])

    save_csv_to_s3(df=done_shop_ids_df, bucket=bucket, path=done_shop_ids_path)


def main():
    save_global_feature_tests_to_s3(end_date="2022-08-29")


if __name__ == "__main__":
    main()
