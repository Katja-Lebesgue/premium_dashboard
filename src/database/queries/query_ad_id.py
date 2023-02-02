import sys

sys.path.append("././.")

from src.utils.help_functions import element_to_list


import pandas as pd
from datetime import date


from src.database.myDB import DBConnect
from src.database.session import SessionLocal

from src.database.models.facebook.facebook_ad import FacebookAd
from src.database.models.facebook.facebook_daily_performance import (
    FacebookDailyPerformance,
)

from sqlalchemy.orm import load_only

from sqlalchemy.orm import defer


def query_ad_id(
    session=SessionLocal(),
    shop_id: str | list[str] = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
) -> pd.DataFrame:

    query = session.query(FacebookAd.ad_id)

    if start_date is not None:
        query = query.join(FacebookDailyPerformance).filter(
            FacebookDailyPerformance.date_start >= start_date,
            FacebookDailyPerformance.date_start <= end_date,
        )

    if shop_id is not None:

        shop_id = element_to_list(shop_id)

        query = query.filter(FacebookAd.shop_id.in_(shop_id))

    query = query.distinct()

    return query


def main():
    session = SessionLocal()
    query = query_ad_id(
        session=session, shop_id="2", start_date="2022-07-01", end_date="2022-07-07"
    )
    ad_ids = pd.read_sql(query.statement, session.bind)["ad_id"]
    print(ad_ids[0:3])
    print(len(ad_ids))


if __name__ == "__main__":
    main()
