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
from src.utils import convert_to_USD, element_to_list, read_query_into_df


class Platform:
    def __init__(self, name: str, ads_insights_model: DeclarativeMeta, account_model: DeclarativeMeta):
        self.name = name
        self.ads_insights_model = ads_insights_model
        self.account_model = account_model


facebook_platform = Platform(
    name="facebook", ads_insights_model=FacebookAdsInsights, account_model=FacebookAdAccount
)
google_platform = Platform(name="google", ads_insights_model=GoogleAdsInsights, account_model=GoogleAdAccount)
tiktok_platform = Platform(name="tiktok", ads_insights_model=TikTokAdsInsights, account_model=TikTokAdAccount)


def ping_ads_insights_by_platform(
    model: DeclarativeMeta,
    account_model: DeclarativeMeta,
    db: Session,
    columns: str | list[str] = ["spend", "revenue"],
    add_platform_prefix: bool = False,
    monthly: bool = True,
    shop_id: int | list[int] | None = None,
    start_date: date | str | None = None,
    end_date: date | str = date.today(),
    add_currency: bool = True,
    conversion_json: dict | None = None,
    convert_to_datetime: bool = True,
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
        query = query.filter(model.date.between(start_date, end_date))

    if add_currency:
        query = query.join(
            account_model,
            (getattr(model, f"{model.platform}_account_id") == getattr(account_model, f"{model.platform}_id"))
            & (model.shop_id == account_model.shop_id),
        )

    query = query.group_by(*group_columns)

    query = query.distinct()

    logger.debug(f"db type: {type(db)}")
    df = read_query_into_df(db=db, query=query)

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

    if monthly and convert_to_datetime:
        df.year_month = df.year_month.apply(lambda x: datetime.strptime(x, "%Y-%m"))

    return df


def ping_ads_insights_all_platforms(
    db: Session,
    columns: str | list[str] = ["spend", "revenue"],
    monthly: bool = True,
    shop_id: int | list[int] | None = None,
    start_date: date | str | None = None,
    end_date: date | str = date.today(),
    get_industry: bool = False,
    convert_to_USD_bool: bool = True,
    pivot: bool = False,
    convert_to_datetime: bool = True,
) -> pd.DataFrame:
    if convert_to_USD_bool:
        conversion_json = crud.currency_exchange_rate.ping_current_rates_dict(db=db)

    add_platform_prefix = not pivot
    for idx, platform in enumerate((facebook_platform, google_platform, tiktok_platform)):
        new_df = ping_ads_insights_by_platform(
            model=platform.ads_insights_model,
            account_model=platform.account_model,
            db=db,
            columns=columns,
            monthly=monthly,
            add_platform_prefix=add_platform_prefix,
            shop_id=shop_id,
            start_date=start_date,
            end_date=end_date,
            conversion_json=conversion_json,
            convert_to_datetime=convert_to_datetime,
        )

        if pivot:
            new_df["platform"] = platform.name

        if idx == 0:
            df = new_df
        else:
            if pivot:
                df = pd.concat([df, new_df], axis=0)
            else:
                df = df.merge(new_df, how="outer")
    if get_industry:
        crm = ping_crm()
        crm = crm[["shop_id", "industry"]]
        df = df.merge(crm, on="shop_id", how="left")
        df.industry = df.industry.apply(lambda x: x if type(x) == str else "unknown")
        df.industry = df.industry.replace({"Unknown": "unknown"})

    if not pivot:
        for col in columns:
            df[f"total_{col}"] = df.apply(
                lambda df: np.nansum([df[f"{platform}_{col}"] for platform in PLATFORMS]), axis=1
            )

    return df
