import sys

sys.path.append("././.")

from src.utils.help_functions import element_to_list
from src.database.models import *


import pandas as pd
from datetime import date
from sqlalchemy import and_

from src.utils.decorators import print_execution_time
from src.database.myDB import DBConnect
from src.database.session import SessionLocal

from src.database.models.facebook.ad_creative_features import AdCreativeFeatures


def query_creative(
    session=SessionLocal(),
    shop_id: str | list[str] = None,
    ad_id: str | list[str] = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
) -> pd.DataFrame:

    if all([x is None for x in [ad_id, shop_id, start_date]]):
        print("No filters in query creative!")
        return None

    query = session.query(AdCreativeFeatures)

    if shop_id is not None:
        shop_id = element_to_list(shop_id)
        query = query.filter(AdCreativeFeatures.shop_id.in_(shop_id))

    if ad_id is not None:
        ad_id = element_to_list(ad_id)
        query = query.filter(AdCreativeFeatures.ad_id.in_(ad_id))

    if start_date is not None:

        query = query.join(
            FacebookDailyPerformance,
            and_(
                AdCreativeFeatures.shop_id == FacebookDailyPerformance.shop_id,
                AdCreativeFeatures.account_id == FacebookDailyPerformance.account_id,
                AdCreativeFeatures.ad_id == FacebookDailyPerformance.ad_id,
            ),
        )
        query = query.filter(
            FacebookDailyPerformance.date_start.between(start_date, end_date)
        )

    query = query.distinct()

    return query


def main():
    session = SessionLocal()
    query = query_creative(session=session, start_date="2022-07-01")
    print(str(query))
    df = pd.read_sql(query.statement, session.bind)
    print(df)


if __name__ == "__main__":
    main()
