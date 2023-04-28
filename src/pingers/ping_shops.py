import sys

sys.path.append("././.")

from datetime import date

import pandas as pd
from loguru import logger
from sqlalchemy.orm import Session

from src.models import *
from src.utils.decorators import print_execution_time


@print_execution_time
def ping_shops(
    db: Session,
    model=FacebookAd,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
) -> pd.DataFrame:

    logger.debug("Here I am!")

    if start_date is not None:
        model = FacebookDailyPerformance

    query = db.query(model.shop_id, Shop.name)
    query = query.join(Shop, model.shop_id == Shop.id)

    if start_date is not None:
        query = query.filter(
            FacebookDailyPerformance.date_start >= start_date,
            FacebookDailyPerformance.date_start <= end_date,
        )

    query = query.distinct()

    df = pd.read_sql(query.statement, db.bind)

    return df
