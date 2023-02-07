import pandas as pd
from datetime import date
from sqlalchemy.orm import Session, InstrumentedAttribute, DeclarativeMeta
from sqlalchemy import func
from loguru import logger


from src.utils.decorators import print_execution_time

from src.models import *
from src.utils.common import element_to_list
from src.s3.read_file_from_s3 import read_csv_from_s3


def ping_ads_insights_by_platform(
    model: DeclarativeMeta,
    db: Session,
    columns: str | list[str] = ["spend"],
    add_platform_prefix: bool = False,
    monthly: bool = True,
    shop_id: int | list[int] | None = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
) -> pd.DataFrame:

    group_columns = [
        model.shop_id,
    ]

    if add_platform_prefix:
        prefix = f"{model.platform}_"
    else:
        prefix = ""

    columns = element_to_list(columns)
    preformance_columns = [getattr(model, col) for col in columns]
    performance_columns = [func.sum(col).label(f"{prefix}{col.key}") for col in preformance_columns]

    all_columns = group_columns + performance_columns

    if monthly:
        year_month_col = func.concat(
            func.extract("year", model.date),
            "-",
            func.to_char(func.extract("month", model.date), "fm00"),
        )
        all_columns.append(year_month_col.label("year_month"))
        group_columns.append(year_month_col)

    query = db.query(*all_columns)

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


def ping_ads_insights_all_platforms(
    db: Session,
    columns: str | list[str] = ["spend"],
    monthly: bool = True,
    shop_id: int | list[int] | None = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
    get_industry: bool = False,
) -> pd.DataFrame:

    for idx, model in enumerate([FacebookAdsInsights, TikTokAdsInsights, GoogleAdsInsights]):
        new_df = ping_ads_insights_by_platform(
            model=model,
            db=db,
            columns=columns,
            monthly=monthly,
            add_platform_prefix=True,
            shop_id=shop_id,
            start_date=start_date,
            end_date=end_date,
        )
        if idx == 0:
            df = new_df
        else:
            df = df.merge(new_df, how="outer")
        if get_industry:
            crm = read_csv_from_s3(bucket="lebesgue-crm", path="crm_dataset_dev.csv", add_global_path=False)
            crm = crm[["shop_id", "industry"]]
            df = df.merge(crm, on="shop_id", how="left")

    return df
