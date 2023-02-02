import sys

sys.path.append("././.")

import pandas as pd

from sqlalchemy import and_

from src.database.queries import *
from src.database.models import *
from src.database.session import *


def ping_raw_creative_and_target(
    session=SessionLocal(), ad_id: str = None, shop_id: str = None
):

    creative_query = query_raw_creative_data(
        session=session, ad_id=ad_id, shop_id=shop_id
    )
    target_query = query_target(session=session, shop_id=shop_id).subquery()

    query = creative_query.join(
        target_query,
        and_(
            FacebookAd.shop_id == target_query.c.shop_id,
            FacebookAd.adset_id == target_query.c.adset_id,
            FacebookAd.account_id == target_query.c.account_id,
        ),
    ).add_columns(target_query)

    df = pd.read_sql(query.statement, session.bind)

    return df


def main():
    session = SessionLocal()
    df = ping_raw_creative_and_target(session=session, shop_id=16038)
    print(df[["countries", "target", "targeting"]])


if __name__ == "__main__":
    main()
