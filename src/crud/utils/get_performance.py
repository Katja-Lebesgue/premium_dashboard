from datetime import date, datetime

import numpy as np
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeMeta, Session

from src.models import *
from src.schemas.facebook.facebook_daily_performance import *
from src.utils import *

column_label_dict = {
    "spend": "spend",
    "impressions": "impr",
    "clicks_": "clicks",
    "purch_": "purch",
    "purch_value_": "purch_value",
}

money_columns = ("spend", "purch_value")

performance_columns = ["spend_USD", "purch_value_USD", "purch", "clicks", "impr"]


def get_performance(
    performance_model: DeclarativeMeta,
    account_model: DeclarativeMeta,
    db: Session,
    shop_id: str | list[str],
    ad_id: str | list[str] = None,
    start_date: date | str | None = None,
    end_date: date | str = date.today(),
    period: Period = Period.year_month,
    cast_to_date: bool = False,
    extra_column_names: list[str] = [],
) -> pd.DataFrame:
    if shop_id is None and ad_id is None:
        raise ValueError("Both shop_id and ad_id is None!")

    start_date, end_date = to_date(start_date), to_date(end_date)

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

    if period == Period.year_month:
        period_col = func.concat(
            func.extract("year", performance_model.date_start),
            "-",
            func.to_char(func.extract("month", performance_model.date_start), "fm00"),
        )
    if period == Period.date:
        period_col = performance_model.date_start

    if period != Period.all:
        columns.append(period_col.label(f"{period}"))
        group_columns.append(period_col)
    else:
        columns.append(func.count(performance_model.ad_id).label("days_active"))

    query = db.query(*columns)

    filters = []

    if ad_id is not None:
        ad_id = element_to_list(ad_id)

        filters.append(performance_model.ad_id.in_(ad_id))

    if shop_id is not None:
        shop_id = element_to_list(shop_id)
        filters.append(performance_model.shop_id.in_(shop_id))

    if start_date is not None:
        filters.append(performance_model.date_start.between(start_date, end_date))

    query = query.filter(*filters).group_by(*group_columns)

    df = read_query_into_df(db=db, query=query)

    if not len(df):
        return df

    metric_columns = list(column_label_dict.values())
    df[metric_columns] = df[metric_columns].fillna(0)

    account_ids = df.account_id.unique().tolist()
    conversion_rates_dict = get_conversion_rates_dict(
        db=db, account_model=account_model, account_id=account_ids
    )
    df = df[df.apply(lambda row: (row.shop_id, row.account_id) in conversion_rates_dict.keys(), axis=1)]
    if not len(df):
        return df
    for column in money_columns:
        df[f"{column}_USD"] = df.apply(
            lambda row: row[column] / conversion_rates_dict.get((row.shop_id, row.account_id), np.inf), axis=1
        )

    if cast_to_date and period == Period.year_month:
        df[f"{period}"] = df[f"{period}"].apply(lambda x: datetime.strptime(x, "%Y-%m").date())

    return df


def get_conversion_rates_dict(
    db: Session, account_model: DeclarativeMeta, account_id: str | list[str]
) -> dict:
    account_id = element_to_list(account_id)
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
            account_model.shop_id,
            account_model.currency,
            conversion_rates_subquery.c.rate_from_usd,
        )
        .join(conversion_rates_subquery, conversion_rates_subquery.c.code == account_model.currency)
        .filter(account_model.channel_account_id.in_(account_id), conversion_rates_subquery.c.date_rank == 1)
    )

    return {(row.shop_id, row.channel_account_id): row.rate_from_usd for row in query.all()}
