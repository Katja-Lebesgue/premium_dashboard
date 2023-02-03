import pandas as pd
from datetime import date, datetime
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.utils.decorators import print_execution_time


from src.models import *
from src.crud import *
from src.database.session import SessionLocal
from src.pingers.ping_creative import ping_creative

from src.feature_extractors import *


# @print_execution_time
def ping_creative_and_performance(
    db: Session,
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
        db=db,
        shop_id=shop_id,
        ad_id=ad_id,
        start_date=start_date,
        end_date=end_date,
        get_aov=get_aov,
        get_industry=get_industry,
    )

    if len(creative) == 0:
        return creative

    performance_query = crud_fb_daily_performance.query_performance(
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

    if add_performance_columns_bool:
        performance = add_performance_columns(performance)

    performance.shop_id = performance.shop_id.astype(str)

    if monthly and cast_to_date:
        performance["year_month"] = performance.year_month.apply(lambda x: datetime.strptime(x, "%Y-%m"))

    df = creative.merge(performance)

    return df
