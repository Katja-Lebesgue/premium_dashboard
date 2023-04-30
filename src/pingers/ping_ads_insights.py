from datetime import date, datetime

import numpy as np
import pandas as pd
from loguru import logger
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeMeta, Session

from src import crud
from src.models import *
from src.models.enums.EPlatform import PLATFORMS
from src.pingers.ping_crm import ping_crm
from src.utils import convert_to_USD, element_to_list


def ping_ads_insights_by_platform(
    model: DeclarativeMeta,
    account_model: DeclarativeMeta,
    db: Session,
    columns: str | list[str] = ["spend", "revenue"],
    add_platform_prefix: bool = False,
    monthly: bool = True,
    shop_id: int | list[int] | None = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
    add_currency: bool = True,
    conversion_json: dict | None = None,
) -> pd.DataFrame:
    if conversion_json is not None:
        add_currency = True

    group_columns = [
        model.shop_id,
    ]

    if add_currency:
        group_columns.append(account_model.currency)

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

    if add_currency:
        query = query.join(
            account_model,
            (getattr(model, f"{model.platform}_account_id") == getattr(account_model, f"{model.platform}_id"))
            & (model.shop_id == account_model.shop_id),
        )

    query = query.group_by(*group_columns)

    query = query.distinct()

    logger.debug(f"db type: {type(db)}")
    df = pd.read_sql(query.statement, db.bind)

    if conversion_json is not None:
        columns = [f"{prefix}{col}" for col in columns]
        for col in columns:
            df[col] = df.apply(
                lambda df: convert_to_USD(
                    price=df[col],
                    currency=df.currency,
                    conversion_rates_dict=conversion_json,
                ),
                axis=1,
            )

    if monthly:
        df.year_month = df.year_month.apply(lambda x: datetime.strptime(x, "%Y-%m"))

    return df


def ping_ads_insights_all_platforms(
    db: Session,
    columns: str | list[str] = ["spend"],
    monthly: bool = True,
    shop_id: int | list[int] | None = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
    get_industry: bool = False,
    convert_to_USD_bool: bool = True,
) -> pd.DataFrame:
    if convert_to_USD_bool:
        conversion_json = crud.currency_exchange_rate.ping_current_rates_dict(db=db)

    for idx, (model, account_model) in enumerate(
        zip(
            [FacebookAdsInsights, TikTokAdsInsights, GoogleAdsInsights],
            [FacebookAdAccount, TikTokAdAccount, GoogleAdAccount],
        ),
    ):
        new_df = ping_ads_insights_by_platform(
            model=model,
            account_model=account_model,
            db=db,
            columns=columns,
            monthly=monthly,
            add_platform_prefix=True,
            shop_id=shop_id,
            start_date=start_date,
            end_date=end_date,
            conversion_json=conversion_json,
        )

        if idx == 0:
            df = new_df
        else:
            df = df.merge(new_df, how="outer")
    if get_industry:
        crm = ping_crm()
        crm = crm[["shop_id", "industry"]]
        df = df.merge(crm, on="shop_id", how="left")
        df.industry = df.industry.apply(lambda x: x if type(x) == str else "unknown")
        df.industry = df.industry.replace({"Unknown": "unknown"})

    for col in columns:
        df[f"total_{col}"] = df.apply(
            lambda df: np.nansum([df[f"{platform}_{col}"] for platform in PLATFORMS]), axis=1
        )

    return df
