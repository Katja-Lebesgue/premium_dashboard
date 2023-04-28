import uuid

import pandas as pd

from src.database.session import SessionLocal
from src.image_analysis.utils import *
from src.models import *
from src.s3.utils import *

db = SessionLocal()


def initialize_image_df(
    self,
    performance_df_path: str = "data/fb_images/top_n_ads_per_shop_and_month_by_spend.csv",
    table_path: str = "data/fb_images/image.csv",
):
    table_path = self.image_df
    performance_df = read_csv_from_s3(performance_df_path)

    list_of_objects = list_objects_from_prefix(prefix=table_path)
    if len(list_of_objects):
        old_image_df = read_csv_from_s3(path=table_path)
    else:
        old_image_df = pd.DataFrame(columns=["url", "uuid", "uploaded"])

    new_urls = performance_df.loc[performance_df.url.isin(old_image_df.url), "url"]
    new_image_df = pd.DataFrame(new_urls, columns=["url"])
    new_image_df["uuid"] = new_image_df.url.apply(lambda x: uuid.uuid1())
    new_image_df["uploaded"] = None
    image_df = pd.concat([old_image_df, new_image_df])

    logger.debug(f"old: {len(old_image_df)}, new: {len(new_image_df)}")

    # save_csv_to_s3(df=image_df, path=table_path, index=False)
