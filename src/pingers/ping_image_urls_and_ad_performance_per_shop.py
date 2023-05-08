from sqlalchemy.orm import Session
from datetime import date, datetime

from src import crud
from src.utils import *


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
