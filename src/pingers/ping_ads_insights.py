from datetime import date, datetime

import numpy as np
import pandas as pd
from loguru import logger
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeMeta, Session
from pydantic import BaseModel

from src import crud
from src.models import *
from src.models.enums.EPlatform import PLATFORMS
from src.pingers.ping_crm import ping_crm
from src.utils import convert_to_USD, element_to_list, read_query_into_df
from src.crud.utils.get_performance import column_label_dict, money_columns


class Platform(BaseModel):
    name: str
    ads_insights_model: DeclarativeMeta
    account_model: DeclarativeMeta

    class Config:
        arbitrary_types_allowed = True


facebook_platform = Platform(
    name="facebook", ads_insights_model=FacebookAdsInsights, account_model=FacebookAdAccount
)
google_platform = Platform(name="google", ads_insights_model=GoogleAdsInsights, account_model=GoogleAdAccount)
tiktok_platform = Platform(name="tiktok", ads_insights_model=TikTokAdsInsights, account_model=TikTokAdAccount)

PLATFORMS = (facebook_platform, google_platform, tiktok_platform)


def ping_ads_insights_by_platform(
    platform: Platform,
    db: Session,
    columns: str | list[str] = ["spend", "purch_value", "impr", "clicks", "purch"],
    monthly: bool = True,
    shop_id: int | list[int] | None = None,
    start_date: date | str | None = None,
    end_date: date | str = date.today(),
    add_currency: bool = True,
    conversion_json: dict | None = None,
    convert_to_datetime: bool = True,
) -> pd.DataFrame:
    model = platform.ads_insights_model
    account_model = platform.account_model

    if conversion_json is not None:
        add_currency = True

    group_columns = [
        model.shop_id,
    ]

    if add_currency:
        group_columns.append(account_model.currency)

    columns = element_to_list(columns)
    performance_columns = [
        func.sum(getattr(model, col)).label(label)
        for col, label in column_label_dict.items()
        if label in columns
    ]

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
        query = query.filter(model.date.between(start_date, end_date))

    if add_currency:
        query = query.join(
            account_model,
            (getattr(model, f"{platform.name}_account_id") == getattr(account_model, f"{platform.name}_id"))
            & (model.shop_id == account_model.shop_id),
        )

    query = query.group_by(*group_columns)

    query = query.distinct()

    df = read_query_into_df(db=db, query=query)

    if conversion_json is not None:
        for col in set(columns).intersection(money_columns):
            df[f"{col}_USD"] = df.apply(
                lambda df: convert_to_USD(
                    price=df[col],
                    currency=df.currency,
                    conversion_rates_dict=conversion_json,
                ),
                axis=1,
            )

    if monthly and convert_to_datetime:
        df.year_month = df.year_month.apply(lambda x: datetime.strptime(x, "%Y-%m"))

    df["platform"] = platform.name

    return df


def ping_ads_insights_all_platforms(
    db: Session,
    columns: str | list[str] = ["spend", "purch_value", "impr", "clicks", "purch"],
    monthly: bool = True,
    shop_id: int | list[int] | None = None,
    start_date: date | str | None = None,
    end_date: date | str = date.today(),
    get_industry: bool = False,
    convert_to_USD_bool: bool = True,
    convert_to_datetime: bool = True,
) -> pd.DataFrame:
    if convert_to_USD_bool:
        conversion_json = crud.currency_exchange_rate.ping_current_rates_dict(db=db)

    df = pd.DataFrame()
    for platform in PLATFORMS:
        new_df = ping_ads_insights_by_platform(
            platform=platform,
            db=db,
            columns=columns,
            monthly=monthly,
            shop_id=shop_id,
            start_date=start_date,
            end_date=end_date,
            conversion_json=conversion_json,
            convert_to_datetime=convert_to_datetime,
        )

        df = pd.concat([df, new_df], axis=0)

    df = df.fillna(0)

    if get_industry:
        crm = ping_crm()
        crm = crm[["shop_id", "industry"]]
        df = df.merge(crm, on="shop_id", how="left")
        df.industry = df.industry.apply(lambda x: x if type(x) == str else "unknown")
        df.industry = df.industry.replace({"Unknown": "unknown"})

    return df
