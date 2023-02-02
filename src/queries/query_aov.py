import sys

sys.path.append("././.")

from src.database.models.shopify.shopify_order import ShopifyOrder

import pandas as pd
from sqlalchemy import func, cast, Float
from datetime import date

from src.database.session import SessionLocal
from src.database.models.facebook.facebook_daily_performance import (
    FacebookDailyPerformance,
)
from src.database.models.facebook.facebook_ad_account import FacebookAdAccount
from src.utils.help_functions import element_to_list


def query_aov(
    session=SessionLocal(),
    shop_id: str | list[str] = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
) -> pd.DataFrame:

    columns = [
        ShopifyOrder.shop_id,
        func.avg(cast(ShopifyOrder.total_price_usd, Float())).label("aov"),
    ]

    query = session.query(*columns)

    if shop_id is not None:
        shop_id = element_to_list(shop_id)
        query = query.filter(ShopifyOrder.shop_id.in_(shop_id))

    if start_date is not None:
        query = query.filter(
            ShopifyOrder.created_at >= start_date,
            ShopifyOrder.created_at <= end_date,
        )

    query = query.group_by(ShopifyOrder.shop_id)

    query = query.distinct()

    return query


def main():
    session = SessionLocal()
    query = query_aov(session=session, shop_id="2", start_date="2022-05-07")
    df = pd.read_sql(query.statement, session.bind)
    print(df)
    print(len(df))


if __name__ == "__main__":
    main()
