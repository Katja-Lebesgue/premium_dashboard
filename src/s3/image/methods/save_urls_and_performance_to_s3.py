from datetime import date, datetime

import pandas as pd
from loguru import logger
from sqlalchemy.orm import Session
from tqdm import tqdm

from src import crud
from src.database.session import SessionLocal
from src.image_analysis.utils import *
from src.models import *
from src.utils import *

db = SessionLocal()


def save_urls_and_performance_to_s3(
    self,
    db: Session,
    force_from_scratch: bool = False,
    end_date: date = date.today(),
    start_date: date = datetime.strptime("2015-01-01", "%Y-%m-%d").date(),
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

    conversion_rates_dict = crud.currency_exchange_rate.ping_current_rates_dict(db=db)

    loader = tqdm(enumerate(shop_ids), total=len(shop_ids))
    for idx, shop_id in loader:
        loader.set_postfix({"shop_id": str(shop_id)})
        new_df = ping_image_urls_and_ad_performance_per_shop(
            db=db, shop_id=shop_id, start_date=start_date, end_date=end_date
        )

        try:
            assert len(new_df) == len(new_df.drop_duplicates(["shop_id", "ad_id", "year_month"]))
        except Exception:
            logger.debug(f"values are not unique for shop {shop_id}")
        df = pd.concat([df, new_df], axis=0)
        if idx % n_iterations_between_save == 5:
            save_csv_to_s3(df=df, path=table_path, index=False)

    save_csv_to_s3(df=df, path=table_path, index=False)


def ping_image_urls_and_ad_performance_per_shop(
    db: Session,
    shop_id: int,
    conversion_rates_dict: dict,
    end_date: date = date.today(),
    start_date: date = datetime.strptime("2015-01-01", "%Y-%m-%d").date(),
):
    fb_ad_query = crud.image.query_fb_ad_ids_and_image_urls_by_shop(
        db=db, shop_id=shop_id, start_date=start_date, end_date=end_date
    )
    fb_ad_df = pd.read_sql(fb_ad_query.statement, db.bind)

    performance_df = pd.DataFrame()
    date_boundary_candidates = [
        date(year=year, month=1, day=1) for year in range(start_date.year, end_date.year + 1)
    ]
    date_range = [dt for dt in date_boundary_candidates if dt < end_date and dt > start_date] + [end_date]
    start = start_date
    for end in date_range:
        performance_query = crud.fb_daily_performance.query_performance(
            db=db,
            shop_id=shop_id,
            start_date=start,
            end_date=end,
            monthly=True,
        )
        new_performance_df = pd.read_sql(performance_query.statement, db.bind)
        performance_df = pd.concat([performance_df, new_performance_df], axis=0)
        start = end

    full_df = fb_ad_df.merge(performance_df, on=["ad_id", "account_id"])

    if not len(full_df):
        return full_df

    full_df["shop_id"] = shop_id
    full_df["spend_USD"] = full_df.apply(
        lambda df: convert_to_USD(
            price=df.spend,
            currency=df.currency,
            conversion_rates_dict=conversion_rates_dict,
        ),
        axis=1,
    )
    return full_df
