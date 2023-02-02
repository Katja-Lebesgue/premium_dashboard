import sys

sys.path.append("././.")

import pandas as pd
import numpy as np

from sqlalchemy import func

from src.s3 import *
from src.database.pingers import *
from src.utils import *
from metadata.globals import *
from tqdm import tqdm


import warnings

warnings.filterwarnings("ignore", message="Mean of empty slice")
warnings.filterwarnings("ignore", message="invalid value encountered in double_scalars")
warnings.filterwarnings(
    "ignore",
    message="The values in the array are unorderable. Pass `sort=False` to suppress this warning.",
)


@print_execution_time
def save_global_descriptive_statistics_to_s3(
    folder=f"data/global/",
    bucket="creative-features",
    csv_file_name: str = None,
    end_date=date.today().strftime("%Y-%m-%d"),
):

    if csv_file_name is None:
        csv_file_name = f"global_descriptive_statistics_{end_date}"

    table_path = folder + csv_file_name + ".csv"

    done_shop_ids_path = folder + csv_file_name + "_done_shop_ids" + ".csv"

    all_shop_ids = ping_shops()["shop_id"]

    group_cols = [
        "year_month",
        "feature",
        "feature_value",
    ]
    print(table_path)
    list_of_objects = list_objects_from_prefix(prefix=table_path)

    print(list_of_objects)

    # table was already created today
    if len(list_of_objects):
        # table was already created today

        table = read_csv_from_s3(path=table_path)
        table.set_index(keys=group_cols, inplace=True)

        done_shop_ids = read_csv_from_s3(path=done_shop_ids_path, bucket=bucket)[
            "shop_id"
        ]

        print(f"we have {len(done_shop_ids)} done shop ids.")

        shop_ids = all_shop_ids[~all_shop_ids.isin(done_shop_ids)]

    else:

        table = pd.DataFrame()
        shop_ids = all_shop_ids

    descriptive_features = boolean_text_features + ["creative_type", "target"]
    metric_columns = [
        "count_ads",
        "spend_USD",
        "impr",
        "link_clicks",
        "purch",
        "roas",
        "cac",
    ]

    for shop_iter, shop_id in tqdm(enumerate(shop_ids), total=len(shop_ids)):

        print(f"iter: {shop_iter}")

        print(f"shop_id: {shop_id}")

        data_shop = ping_creative_and_performance(
            shop_id=shop_id,
            monthly=True,
            cast_to_date=False,
            get_industry=False,
            get_aov=False,
        )

        data_shop["count_ads"] = 1

        if shop_iter % 10 == 5:
            save_csv_to_s3(
                df=table,
                path=table_path,
                bucket=bucket,
            )

            done_shop_ids = shop_ids[: shop_iter - 1]
            done_shop_ids_df = pd.DataFrame(done_shop_ids, columns=["shop_id"])

            save_csv_to_s3(df=done_shop_ids_df, bucket=bucket, path=done_shop_ids_path)

            table.to_csv("./././data/probica.csv")

        if len(data_shop) == 0 or any(
            [x not in data_shop.columns for x in ["spend_USD", "discounts_any"]]
        ):
            continue

        # print(data_shop.columns)
        # print(f"len: {len(data_shop)}")

        data_shop.to_csv("./././data/global_description.csv")

        if any([col not in data_shop.columns for col in descriptive_features]):
            continue

        for col_iter, col in enumerate(descriptive_features):

            grouped = (
                data_shop.rename(columns={col: "feature_value"})
                .groupby(
                    [
                        "year_month",
                        "feature_value",
                    ]
                )
                .sum()
                .loc[:, metric_columns]
            )

            grouped["feature"] = col
            grouped = grouped.set_index(["feature"], append=True)
            grouped = grouped.reorder_levels(group_cols, axis=0)

            grouped["count_shops"] = grouped.count_ads > 0

            if shop_iter == 0 and col_iter == 0:
                table = grouped
            else:
                table = table.add(grouped, fill_value=0)

        print(f"minimal date in new shop: {data_shop.loc[:, 'year_month'].min()}")

        print(
            f"minimal date in table: {table.reset_index().loc[:, 'year_month'].min()}"
        )

    save_csv_to_s3(
        df=table,
        path=table_path,
        bucket=bucket,
    )

    done_shop_ids = all_shop_ids
    done_shop_ids_df = pd.DataFrame(done_shop_ids, columns=["shop_id"])
    save_csv_to_s3(df=done_shop_ids_df, bucket=bucket, path=done_shop_ids_path)

    table.to_csv("./././data/probica.csv")
    return table


def main():
    table = save_global_descriptive_statistics_to_s3()
    print(table)


if __name__ == "__main__":
    main()
