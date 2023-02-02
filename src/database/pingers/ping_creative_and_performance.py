import sys

sys.path.append("././.")

from tracemalloc import start
import pandas as pd
from datetime import date, datetime
from sqlalchemy import and_

from src.utils.decorators import print_execution_time

from src.database.queries import *
from src.database.models import *
from src.database.session import SessionLocal
from src.database.pingers.ping_creative import ping_creative

from src.feature_extractors import *


# join on the base, don't know how to unstack this one

# @print_execution_time
# def ping_creative_and_performance(
#     session=None,
#     ad_id: str | list[str] = None,
#     shop_id: str | list[str] = None,
#     start_date: str = None,
#     end_date: str = date.today().strftime("%Y-%m-%d"),
# ) -> pd.DataFrame:

#     if session is None:
#         session = SessionLocal()

#     if all([x is None for x in [ad_id, shop_id, start_date]]):
#         print("No filters!")
#         return None

#     creative_query = query_creative(session=session, shop_id=shop_id, ad_id=ad_id)
#     performance_query = query_monthly_performance(
#         session=session,
#         shop_id=shop_id,
#         ad_id=ad_id,
#         start_date=start_date,
#         end_date=end_date,
#     ).subquery()

#     query = creative_query.join(
#         performance_query,
#         and_(
#             AdCreativeFeatures.shop_id == performance_query.c.shop_id,
#             AdCreativeFeatures.ad_id == performance_query.c.ad_id,
#             AdCreativeFeatures.account_id == performance_query.c.account_id,
#         ),
#     ).add_columns(performance_query)

#     df = pd.read_sql(query.statement, session.bind)

#     df = add_performance_columns(df)

#     return df


# @print_execution_time
def ping_creative_and_performance(
    session=SessionLocal(),
    ad_id: str | list[str] = None,
    shop_id: str | list[str] = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
    monthly: bool = True,
    get_aov: bool = True,
    get_industry: bool = True,
    cast_to_date: bool = True,
    add_performance_columns_bool: bool = True,
) -> pd.DataFrame:

    if all([x is None for x in [ad_id, shop_id, start_date]]):
        print("No filters in ping_creative_and_performance!")
        return None

    creative = ping_creative(
        session=session,
        shop_id=shop_id,
        ad_id=ad_id,
        start_date=start_date,
        end_date=end_date,
        get_aov=get_aov,
        get_industry=get_industry,
    )

    if len(creative) == 0:
        return creative

    performance_query = query_performance(
        session=session,
        shop_id=shop_id,
        ad_id=ad_id,
        start_date=start_date,
        end_date=end_date,
        monthly=monthly,
    )

    performance = pd.read_sql(performance_query.statement, session.bind)

    if len(performance) == 0:
        return creative

    if add_performance_columns_bool:
        performance = add_performance_columns(performance)

    performance.shop_id = performance.shop_id.astype(str)

    if monthly and cast_to_date:
        performance["year_month"] = performance.year_month.apply(
            lambda x: datetime.strptime(x, "%Y-%m")
        )

    df = creative.merge(performance)

    return df


def main():
    session = SessionLocal()
    df = ping_creative_and_performance(session=session, shop_id="2")
    print(df)


if __name__ == "__main__":
    main()
