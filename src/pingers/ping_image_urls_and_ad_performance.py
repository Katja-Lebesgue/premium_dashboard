from sqlalchemy.orm import Session
from datetime import date, datetime

from src import crud
from src.utils import *


def ping_image_urls_and_ad_performance(
    db: Session,
    shop_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
):
    fb_ad_df = crud.image.get_fb_ad_ids_and_image_urls_by_shop(db=db, shop_id=shop_id)

    if not len(fb_ad_df):
        return fb_ad_df

    performance_df = crud.fb_daily_performance.get_performance(
        db=db,
        shop_id=shop_id,
        ad_id=fb_ad_df.ad_id.unique().tolist(),
        start_date=start_date,
        end_date=end_date,
    )

    full_df = fb_ad_df.merge(performance_df, on=["ad_id", "account_id", "shop_id"])

    return full_df
