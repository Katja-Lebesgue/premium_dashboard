import sys

sys.path.append("././.")

from datetime import date

import pandas as pd
from loguru import logger
from sqlalchemy.orm import Session

from src.models import *
from src.utils import *


@print_execution_time
def ping_shops(
    db: Session,
    model=FacebookAd,
    start_date: date | str | None = None,
    end_date: date | str = date.today(),
) -> pd.DataFrame:
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
