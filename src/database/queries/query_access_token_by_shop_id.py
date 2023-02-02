import sys

sys.path.append("././.")

from src.utils.help_functions import element_to_list


import pandas as pd
from datetime import date
from sqlalchemy import func


from src.database.myDB import DBConnect
from src.database.session import SessionLocal

from src.database.models.credentials import Credentials
from src.database.models.facebook.facebook_daily_performance import (
    FacebookDailyPerformance,
)

from sqlalchemy.orm import load_only

from sqlalchemy.orm import defer


def query_access_token_by_shop_id(
    session=None,
    shop_id: str | list[str] = None,
) -> pd.DataFrame:

    if session is None:
        session = SessionLocal()

    subquery = session.query(
        Credentials.access_token,
        Credentials.shop_id,
        func.rank()
        .over(
            order_by=Credentials.created_date_time.desc(),
            partition_by=Credentials.shop_id,
        )
        .label("rnk"),
    ).filter(
        Credentials.credentials_provider == "FACEBOOK",
        Credentials.expired == False,
    )

    if shop_id is not None:
        shop_id = element_to_list(shop_id)
        subquery = subquery.filter(Credentials.shop_id.in_(shop_id))

    subquery = subquery.subquery()

    query = session.query(subquery).filter(subquery.c.rnk == 1)

    query = query.distinct()

    return query


def main():
    session = SessionLocal()
    query = query_access_token_by_shop_id(session=session, shop_id="2")
    df = pd.read_sql(query.statement, session.bind)
    print(df)


if __name__ == "__main__":
    main()
