from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session, DeclarativeMeta

from loguru import logger
import pandas as pd
import numpy as np


from src.models import *
from src.schemas.facebook.facebook_daily_performance import *
from src.utils import element_to_list


column_label_dict = {
    "spend": "spend",
    "impressions": "impr",
    "clicks_": "clicks",
    "purch_": "purch",
    "purch_value_": "purch_value",
}

money_columns = ("spend", "purch_value")


def get_performance(
    performance_model: DeclarativeMeta,
    account_model: DeclarativeMeta,
    db: Session,
    shop_id: str | list[str],
    ad_id: str | list[str] = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
    monthly: bool = True,
    cast_to_date: bool = False,
    extra_column_names: list[str] = [],
) -> pd.DataFrame:
    extra_columns = [getattr(performance_model, column) for column in extra_column_names]
    group_columns = [
        performance_model.ad_id,
        performance_model.shop_id,
        performance_model.account_id,
        performance_model.adgroup_id_,
    ] + extra_columns

    performance_columns = [
        func.sum(getattr(performance_model, col)).label(label) for col, label in column_label_dict.items()
    ]

    columns = group_columns + performance_columns

    if monthly:
        year_month_col = func.concat(
            func.extract("year", performance_model.date_start),
            "-",
            func.to_char(func.extract("month", performance_model.date_start), "fm00"),
        )
        columns.append(year_month_col.label("year_month"))
        group_columns.append(year_month_col)

    query = db.query(*columns)

    if ad_id is not None:
        ad_id = element_to_list(ad_id)
        query = query.filter(performance_model.ad_id.in_(ad_id))

    if shop_id is not None:
        shop_id = element_to_list(shop_id)
        query = query.filter(performance_model.shop_id.in_(shop_id))

    if start_date is not None:
        query = query.filter(
            performance_model.date_start >= start_date,
            performance_model.date_start <= end_date,
        )

    query = query.group_by(*group_columns)

    query = query.distinct()

    df = pd.read_sql(query.statement, db.bind)

    if not len(df):
        return df

    metric_columns = list(column_label_dict.values())
    df[metric_columns] = df[metric_columns].fillna(0)

    conversion_rates_dict = get_conversion_rates_dict(db=db, account_model=account_model, shop_id=shop_id)
    df = df[df.account_id.isin(conversion_rates_dict.keys())]
    if not len(df):
        return df
    for column in money_columns:
        df[f"{column}_USD"] = df.apply(
            lambda df_: df_[column] / conversion_rates_dict.get(df_["account_id"], np.inf), axis=1
        )

    if cast_to_date and monthly:
        df["year_month"] = df.year_month.apply(lambda x: datetime.strptime(x, "%Y-%m"))

    return df


def get_conversion_rates_dict(db: Session, account_model: DeclarativeMeta, shop_id: int | list[int]) -> dict:
    shop_id = element_to_list(shop_id)
    conversion_rates_subquery = (
        db.query(
            CurrencyExchangeRate.code,
            CurrencyExchangeRate.rate_from_usd,
            func.rank()
            .over(partition_by=CurrencyExchangeRate.code, order_by=CurrencyExchangeRate.date.desc())
            .label("date_rank"),
        ).order_by(CurrencyExchangeRate.code, CurrencyExchangeRate.date.desc())
    ).subquery()

    query = (
        db.query(
            account_model.channel_account_id,
            account_model.currency,
            conversion_rates_subquery.c.rate_from_usd,
        )
        .join(conversion_rates_subquery, conversion_rates_subquery.c.code == account_model.currency)
        .filter(account_model.shop_id.in_(shop_id), conversion_rates_subquery.c.date_rank == 1)
    )

    return {row.channel_account_id: row.rate_from_usd for row in query.all()}
