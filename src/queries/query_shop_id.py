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


def query_shop_id(
    session=SessionLocal(),
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
) -> pd.DataFrame:

    query = session.query(FacebookAd.shop_id)

    if start_date is not None:
        query = query.join(FacebookDailyPerformance).filter(
            FacebookDailyPerformance.date_start >= start_date,
            FacebookDailyPerformance.date_start <= end_date,
        )

    query = query.distinct()

    return query


def main():
    session = SessionLocal()
    query = query_shop_id(
        session=session, start_date="2022-07-01", end_date="2022-07-07"
    )
    shop_ids = pd.read_sql(query.statement, session.bind)["shop_id"]

    print(shop_ids)
    print(len(shop_ids))


if __name__ == "__main__":
    main()
