import sys

sys.path.append("././.")

from tracemalloc import start
import pandas as pd
from datetime import date
from sqlalchemy import and_

from src.utils.decorators import print_execution_time

from src.s3 import *
from src.database.queries import *
from src.database.models import *
from src.database.session import SessionLocal


# @print_execution_time
def ping_creative(
    session=None,
    ad_id: str | list[str] = None,
    shop_id: str | list[str] = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
    get_aov: str = True,
    get_industry: bool = True,
) -> pd.DataFrame:

    if session is None:
        session = SessionLocal()

    if all([x is None for x in [ad_id, shop_id, start_date]]):
        print("No filters in ping creative!")
        return None

    query = query_creative(
        session=session,
        shop_id=shop_id,
        ad_id=ad_id,
        start_date=start_date,
        end_date=end_date,
    )
    if get_aov:
        aov_query = query_aov(
            session=session, shop_id=shop_id, start_date=start_date, end_date=end_date
        ).subquery()

        query = query.join(
            aov_query, AdCreativeFeatures.shop_id == aov_query.c.shop_id
        ).add_columns(aov_query.c.aov)

    df = pd.read_sql(query.statement, session.bind)

    df.shop_id = df.shop_id.astype(str)

    if get_industry:
        crm = read_csv_from_s3(
            bucket="lebesgue-crm", path="crm_dataset_dev.csv", add_global_path=False
        )
        crm = crm[["shop_id", "industry"]]
        df = df.merge(crm, how="left")

    # unstacking
    index = list(df.columns)
    index.remove("value")
    index.remove("feature")
    index.append("feature")
    df.set_index(index, inplace=True)

    df = df.unstack(level=-1)
    df = df.droplevel(level=0, axis=1)
    df = df.reset_index()
    df.columns.name = None

    return df


def main():
    session = SessionLocal()
    df = ping_creative(session=session, shop_id=["2", "16038"])
    print(df.columns)
    print(df.aov)


if __name__ == "__main__":
    main()
