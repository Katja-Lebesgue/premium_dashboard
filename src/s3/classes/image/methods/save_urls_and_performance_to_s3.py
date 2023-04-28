from datetime import date

import pandas as pd
from loguru import logger
from sqlalchemy.orm import Session
from tqdm import tqdm

from src.crud.media.image import image as cr_image
from src.database.session import SessionLocal
from src.image_analysis.utils import *
from src.models import *
from src.s3.utils import read_csv_from_s3, save_csv_to_s3, list_objects_from_prefix

db = SessionLocal()


def save_urls_and_performance_to_s3(
    self,
    db: Session,
    force_from_scratch: bool = False,
    start_date: date | None = None,
    end_date: date | None = None,
    monthly: bool = True,
    n_iterations_between_save: int = 20,
):
    table_path = self.url_performance_df
    shop_ids = db.query(Image.shop_id).filter(Image.source == "facebook").distinct().all()
    shop_ids = pd.Series([row.shop_id for row in shop_ids])
    shop_ids = shop_ids.sort_values()

    df = pd.DataFrame()

    list_of_objects = list_objects_from_prefix(prefix=table_path)
    from_scratch = len(list_of_objects) == 0 or force_from_scratch

    if not from_scratch:
        df = read_csv_from_s3(table_path)
        max_done_shop_id = df.shop_id.max()
        shop_ids = shop_ids[shop_ids > max_done_shop_id]
        logger.debug(f"len(df): {len(df)}, len(shop_ids to go): {len(shop_ids)}")
    else:
        df = pd.DataFrame()

    loader = tqdm(enumerate(shop_ids), total=len(shop_ids))
    for idx, shop_id in loader:
        loader.set_postfix({"shop_id": str(shop_id)})
        new_df = cr_image.ping_fb_urls_by_shop(
            db=db,
            shop_id=shop_id,
            start_date=start_date,
            end_date=end_date,
            performance_columns=self.performance_columns,
            monthly=monthly,
        )

        try:
            assert len(new_df) == len(new_df.drop_duplicates(["shop_id", "ad_id", "year_month"]))
        except Exception:
            logger.debug(f"values are not unique for shop {shop_id}")
        df = pd.concat([df, new_df], axis=0)
        if idx % n_iterations_between_save == 5:
            save_csv_to_s3(df=df, path=table_path, index=False)

    save_csv_to_s3(df=df, path=table_path, index=False)
