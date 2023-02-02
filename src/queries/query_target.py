import sys

sys.path.append("././.")

from src.utils.help_functions import element_to_list


import pandas as pd
from datetime import date


from src.database.myDB import DBConnect
from src.database.session import SessionLocal

from src.database.models.facebook.facebook_adset import FacebookAdset
from src.database.models.facebook.facebook_daily_performance import (
    FacebookDailyPerformance,
)

from sqlalchemy.orm import Session

from sqlalchemy.orm import load_only

from sqlalchemy.orm import defer


def query_target(
    session: Session,
    adset_id: str | list[str] | None = None,
    account_id: str | list[str] | None = None,
    shop_id: int | list[int] | None = None,
) -> pd.DataFrame:

    query = session.query(
        FacebookAdset.adset_id,
        FacebookAdset.account_id,
        FacebookAdset.shop_id,
        FacebookAdset.target,
        FacebookAdset.targeting,
        FacebookAdset.targeting["geo_locations"]["countries"].label("countries"),
        FacebookAdset.targeting["age_max"].label("age_max"),
        FacebookAdset.targeting["age_min"].label("age_min"),
        FacebookAdset.targeting["custom_audiences"].label("custom_audiences"),
    )

    if shop_id is not None:
        shop_id = element_to_list(shop_id)
        query = query.filter(FacebookAdset.shop_id.in_(shop_id))

    if account_id is not None:
        account_id = element_to_list(account_id)
        query = query.filter(FacebookAdset.account_id.in_(account_id))

    if adset_id is not None:
        adset_id = element_to_list(adset_id)
        query = query.filter(FacebookAdset.adset_id.in_(adset_id))

    query = query.distinct()

    return query


def main():
    session = SessionLocal()
    query = query_target(
        session=session,
        shop_id="16038",
    )
    df = pd.read_sql(query.statement, session.bind)
    print(df)
    print(len(df))


if __name__ == "__main__":
    main()
