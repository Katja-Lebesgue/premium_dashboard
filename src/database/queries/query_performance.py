import sys

sys.path.append("././.")

import pandas as pd
from sqlalchemy import func
from datetime import date

from src.database.session import SessionLocal
from src.database.models.facebook.facebook_daily_performance import (
    FacebookDailyPerformance,
)
from src.database.models.facebook.facebook_ad_account import FacebookAdAccount
from src.utils.help_functions import element_to_list


def query_performance(
    session=SessionLocal(),
    shop_id: str | list[str] = None,
    ad_id: str | list[str] = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
    add_currency: bool = True,
    monthly: bool = True,
) -> pd.DataFrame:

    group_columns = [
        FacebookDailyPerformance.ad_id,
        FacebookDailyPerformance.shop_id,
        FacebookDailyPerformance.account_id,
    ]

    performance_columns = [
        func.sum(FacebookDailyPerformance.impressions).label("impr"),
        func.sum(FacebookDailyPerformance.link_clicks).label("link_clicks"),
        func.sum(FacebookDailyPerformance.purchases).label("purch"),
        func.sum(FacebookDailyPerformance.spend).label("spend"),
        func.sum(FacebookDailyPerformance.purchases_conversion_value).label(
            "purch_value"
        ),
    ]

    columns = group_columns + performance_columns

    if monthly:
        year_month_col = func.concat(
            func.extract("year", FacebookDailyPerformance.date_start),
            "-",
            func.to_char(
                func.extract("month", FacebookDailyPerformance.date_start), "fm00"
            ),
        )
        columns.append(year_month_col.label("year_month"))
        group_columns.append(year_month_col)

    if add_currency:
        columns.append(FacebookAdAccount.currency)
        group_columns.append(FacebookAdAccount.currency)

    query = session.query(*columns)

    if ad_id is not None:
        ad_id = element_to_list(ad_id)
        query = query.filter(FacebookDailyPerformance.ad_id.in_(ad_id))

    if shop_id is not None:
        shop_id = element_to_list(shop_id)
        query = query.filter(FacebookDailyPerformance.shop_id.in_(shop_id))

    if start_date is not None:
        query = query.filter(
            FacebookDailyPerformance.date_start >= start_date,
            FacebookDailyPerformance.date_start <= end_date,
        )

    query = query.group_by(*group_columns)

    if add_currency:
        query = query.join(
            FacebookAdAccount,
            FacebookDailyPerformance.account_id == FacebookAdAccount.facebook_id,
        )

    query = query.distinct()

    # query = f"""
    # select perf.ad_id,
    #     perf.shop_id,
    #     perf.account_id,
    #     acc.currency,
    #     extract(year from perf.date_start) || '-' || extract(month from perf.date_start) as year_month,
    #     sum(impressions) as impr,
    #     sum(link_clicks) as link_clicks,
    #     sum(purchases) as purch,
    #     sum(spend) as spend
    # from facebook_daily_performance as perf
    # left join facebook_ad_account as acc
    # on acc.facebook_id = perf.account_id
    # where perf.shop_id in %s
    # and date_start between %s and %s
    # group by perf.ad_id,
    #     perf.shop_id,
    #     perf.account_id,
    #     acc.currency,
    #     extract(year from perf.date_start) || '-' || extract(month from perf.date_start)
    #     """

    return query


def main():
    session = SessionLocal()
    query = query_performance(
        session=session, shop_id="2", start_date="2022-05-07", monthly=False
    )
    df = pd.read_sql(query.statement, session.bind)
    print(df)
    print(len(df))


if __name__ == "__main__":
    main()
