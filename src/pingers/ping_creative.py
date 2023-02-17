from tracemalloc import start
import pandas as pd
from datetime import date
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.utils.decorators import print_execution_time

from src.s3 import *
from src.models import *
from src.crud import *
from src.database.session import SessionLocal


# @print_execution_time
def ping_creative(
    db: Session,
    shop_id: int | list[int],
    ad_id: str | list[str] = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
    get_aov: str = True,
    get_industry: bool = True,
) -> pd.DataFrame:
    query = crud_ad_creative_features.query_creative(
        db=db,
        shop_id=shop_id,
        ad_id=ad_id,
        start_date=start_date,
        end_date=end_date,
    )

    if get_aov:
        aov_query = crud_shopify_order.query_aov(
            db=db, shop_id=shop_id, start_date=start_date, end_date=end_date
        ).subquery()

        query = query.join(aov_query, AdCreativeFeatures.shop_id == aov_query.c.shop_id, isouter=True).add_columns(
            aov_query.c.aov
        )

    df = pd.read_sql(query.statement, db.bind)

    df.shop_id = df.shop_id.astype(str)

    if get_industry:
        crm = read_csv_from_s3(bucket="lebesgue-crm", path="crm_dataset_dev.csv", add_global_path=False)
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
    db = SessionLocal()
    df = ping_creative(db=db, shop_id=["2", "16038"])
    print(df.columns)
    print(df.aov)


if __name__ == "__main__":
    main()
