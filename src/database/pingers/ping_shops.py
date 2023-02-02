import sys

sys.path.append("././.")

import pandas as pd
from datetime import date

from src.utils.decorators import print_execution_time

from src.database.queries import *
from src.database.models import *
from src.database.session import SessionLocal


@print_execution_time
def ping_shops(
    session=None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
) -> pd.DataFrame:

    if session is None:
        session = SessionLocal()

    query = query_shop_id(session=session, start_date=start_date, end_date=end_date)

    query = query.join(Shop, FacebookAd.shop_id == Shop.id).add_columns(Shop.name)
    df = pd.read_sql(query.statement, session.bind)

    df["shop_id"] = df["shop_id"].astype(str)

    return df


def main():
    session = SessionLocal()
    df = ping_shops()
    print(df)


if __name__ == "__main__":
    main()
