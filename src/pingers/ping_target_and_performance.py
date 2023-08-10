from datetime import date, datetime

import pandas as pd
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src import crud
from src.database.session import SessionLocal
from src.feature_extractors import *
from src.models import *
from src.utils import element_to_list
from src.pingers.ping_target import ping_target


def ping_target_and_performance(
    db: Session,
    ad_id: str | list[str] = None,
    shop_id: str | list[str] = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
    monthly: bool = True,
    cast_to_date: bool = True,
    add_performance_columns_bool: bool = True,
) -> pd.DataFrame:
    if all([x is None for x in [ad_id, shop_id, start_date]]):
        print("No filters in ping_target_and_performance!")
        return None

    target_df = ping_target(db=db, ad_id=ad_id, shop_id=shop_id, start_date=start_date, end_date=end_date)

    if len(target_df) == 0:
        return target_df

    performance_query = crud.fb_daily_performance.query_performance(
        db=db,
        shop_id=shop_id,
        ad_id=ad_id,
        start_date=start_date,
        end_date=end_date,
        monthly=monthly,
    )

    performance_df = pd.read_sql(performance_query.statement, db.bind)
    df = target_df.merge(performance_df, on=["adset_id", "account_id", "shop_id"])
    if add_performance_columns_bool:
        df = add_performance_columns(df, db=db)

    if monthly and cast_to_date:
        df["year_month"] = df.year_month.apply(lambda x: datetime.strptime(x, "%Y-%m"))

    return df
