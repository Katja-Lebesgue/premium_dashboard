from datetime import date, datetime

import pandas as pd
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src import crud
from src.database.session import SessionLocal
from src.feature_extractors import *
from src.models import *
from src.utils import element_to_list


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

    performance_subquery = crud.fb_daily_performance.query_performance(
        db=db,
        shop_id=shop_id,
        ad_id=ad_id,
        start_date=start_date,
        end_date=end_date,
        monthly=monthly,
    ).subquery()

    query = db.query(FacebookAdset.targeting, performance_subquery).join(
        performance_subquery,
        (FacebookAdset.adset_id == performance_subquery.c.adset_id)
        & (FacebookAdset.account_id == performance_subquery.c.account_id),
    )

    filters = []

    if ad_id is not None:
        ad_id = element_to_list(ad_id)
        filters.append(FacebookAdset.ad_id.in_(ad_id))
    if shop_id is not None:
        shop_id = element_to_list(shop_id)
        filters.append(FacebookAdset.shop_id.in_(shop_id))
    if len(filters):
        query = query.filter(*filters)

    df = pd.read_sql(query.statement, db.bind)

    if len(df) == 0:
        return df

    if add_performance_columns_bool:
        df = add_performance_columns(df, db=db)

    if monthly and cast_to_date:
        df["year_month"] = df.year_month.apply(lambda x: datetime.strptime(x, "%Y-%m"))

    return df
