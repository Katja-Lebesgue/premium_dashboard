import sys

sys.path.append("././.")

import pandas as pd
import numpy as np

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.database.session import db

from src.s3 import *
from src.pingers import *
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
    db: Session,
    folder=f"data/global/",
    bucket="creative-features",
    csv_file_name: str = None,
    end_date=date.today().strftime("%Y-%m-%d"),
    force_from_scratch: bool = False,
):
    if csv_file_name is None:
        csv_file_name = f"global_descriptive_statistics_{end_date}"

    table_path = folder + csv_file_name + ".csv"

    done_shop_ids_path = folder + csv_file_name + "_done_shop_ids" + ".csv"

    shop_ids_query = db.query(AdCreativeFeatures.shop_id).distinct()
    all_shop_ids = pd.read_sql(shop_ids_query.statement, db.bind)["shop_id"]

    group_cols = [
        "year_month",
        "feature",
        "feature_value",
    ]
    print(table_path)
    list_of_objects = list_objects_from_prefix(prefix=table_path)
    from_scratch = len(list_of_objects) == 0 or force_from_scratch

    print(list_of_objects)

    # table was already created today
    if not from_scratch:
        # table was already created today

        table = read_csv_from_s3(path=table_path)
        table.set_index(keys=group_cols, inplace=True)

        done_shop_ids = read_csv_from_s3(path=done_shop_ids_path, bucket=bucket)["shop_id"].astype(int)

        print(f"we have {len(done_shop_ids)} done shop ids.")

        shop_ids = all_shop_ids[~all_shop_ids.isin(done_shop_ids)]

    else:
        table = pd.DataFrame()
        shop_ids = all_shop_ids

    descriptive_features = boolean_text_features + ["creative_type", "target"]
    metric_columns = ["count_ads", "spend_USD", "impr", "link_clicks", "purch"]

    for shop_iter, shop_id in tqdm(enumerate(shop_ids), total=len(shop_ids)):
        logger.debug(f"shop_id: {shop_id}")

        data_shop = ping_creative_and_performance(
            db=db,
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

            logger.debug(table)

        presence_of_cols = {col: col in data_shop.columns for col in descriptive_features + metric_columns}
        if len(data_shop) == 0 or not all(presence_of_cols.values()):
            logger.debug(
                f"Skipam jer nemam {[col for col in presence_of_cols.keys() if presence_of_cols[col] is False]}"
            )
            continue

        for col_iter, col in enumerate(descriptive_features):
            # for col_iter, col in enumerate(["target"]):
            filtered = data_shop.loc[:, ["year_month", col] + metric_columns].rename(columns={col: "feature_value"})
            sum_by_month = filtered.groupby("year_month").sum()
            grouped = filtered.groupby(
                [
                    "year_month",
                    "feature_value",
                ]
            )

            absolute_sum = grouped.sum().loc[:, metric_columns]
            relative_sum = (absolute_sum / sum_by_month).rename(columns=lambda col_name: col_name + "_by_shop")

            full = absolute_sum.join(relative_sum)

            full["feature"] = col
            full = full.set_index(["feature"], append=True)
            full = full.reorder_levels(group_cols, axis=0).fillna(0)

            # logger.debug(f"full index: {full.index.names}")
            # logger.debug(f"table_index: {table.index.names}")

            full["count_shops"] = (full.count_ads > 0).astype(int)

            if shop_iter == 0 and col_iter == 0 and from_scratch:
                table = full
            else:
                table = table.add(full, fill_value=0)

    save_csv_to_s3(
        df=table,
        path=table_path,
        bucket=bucket,
    )

    done_shop_ids = all_shop_ids
    done_shop_ids_df = pd.DataFrame(done_shop_ids, columns=["shop_id"])
    save_csv_to_s3(df=done_shop_ids_df, bucket=bucket, path=done_shop_ids_path)

    return table


def main():
    table = save_global_descriptive_statistics_to_s3(db=db, force_from_scratch=True)


if __name__ == "__main__":
    main()
