from datetime import date, datetime

import pandas as pd
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src import crud, utils
from src.database.session import SessionLocal
from src.feature_extractors import *
from src.models import *
from src.pingers.ping_facebook_creative_features import ping_facebook_creative


def ping_facebook_creative_and_performance(
    db: Session,
    ad_id: str | list[str] = None,
    shop_id: str | list[str] = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
    monthly: bool = True,
    cast_to_date: bool = True,
) -> pd.DataFrame:
    if all([x is None for x in [ad_id, shop_id, start_date]]):
        print("No filters in ping_facebook_creative_and_performance!")
        return None

    creative = ping_facebook_creative(
        db=db,
        shop_id=shop_id,
        ad_id=ad_id,
        start_date=start_date,
        end_date=end_date,
    )

    if len(creative) == 0:
        return creative

    performance_query = crud.fb_daily_performance.query_performance(
        db=db,
        shop_id=shop_id,
        ad_id=ad_id,
        start_date=start_date,
        end_date=end_date,
        monthly=monthly,
    )

    performance = pd.read_sql(performance_query.statement, db.bind)

    if len(performance) == 0:
        return creative

    performance = add_performance_columns(performance, db=db)

    if monthly and cast_to_date:
        performance["year_month"] = performance.year_month.apply(lambda x: datetime.strptime(x, "%Y-%m"))

    df = creative.merge(performance)

    return df
