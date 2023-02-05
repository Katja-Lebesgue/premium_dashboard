import pandas as pd
from datetime import date
from sqlalchemy.orm import Session, InstrumentedAttribute, DeclarativeMeta
from sqlalchemy import func
from loguru import logger


from src.utils.decorators import print_execution_time

from src.models import *
from src.utils.common import element_to_list


def ping_ads_insights(
    model: DeclarativeMeta,
    columns: InstrumentedAttribute | list[InstrumentedAttribute],
    db: Session,
    monthly: bool = True,
    shop_id: int | list[int] | None = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
) -> pd.DataFrame:

    group_columns = [
        model.shop_id,
    ]

    performance_columns = [func.sum(col).label(col.key) for col in columns]

    columns = group_columns + performance_columns

    if monthly:
        year_month_col = func.concat(
            func.extract("year", model.date),
            "-",
            func.to_char(func.extract("month", model.date), "fm00"),
        )
        columns.append(year_month_col.label("year_month"))
        group_columns.append(year_month_col)

    query = db.query(*columns)

    if shop_id is not None:
        shop_id = element_to_list(shop_id)
        query = query.filter(model.shop_id.in_(shop_id))

    if start_date is not None:
        query = query.filter(
            model.date >= start_date,
            model.date <= end_date,
        )

    query = query.group_by(*group_columns)

    query = query.distinct()

    df = pd.read_sql(query.statement, db.bind)

    return df
