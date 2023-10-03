from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from src.feature_extractors import *
from src.models import *
from src.pingers.ping_facebook_creative_and_performance import ping_facebook_creative_and_performance
from src.pingers.ping_target import ping_target
from src.utils import *


def ping_facebook_creative_target_and_performance(
    db: Session,
    ad_id: str | list[str] = None,
    shop_id: str | list[str] = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
    period: Period = Period.year_month,
    cast_to_date: bool = True,
    enum_to_value: bool = False,
) -> pd.DataFrame:
    if all([x is None for x in [ad_id, shop_id, start_date]]):
        print("No filters in ping_facebook_creative_and_performance!")
        return None

    creative_performance_df = ping_facebook_creative_and_performance(
        db=db,
        shop_id=shop_id,
        ad_id=ad_id,
        start_date=start_date,
        end_date=end_date,
        period=period,
        cast_to_date=cast_to_date,
        enum_to_value=enum_to_value,
    )

    if len(creative_performance_df) == 0:
        return creative_performance_df

    creative_performance_df = creative_performance_df.drop(columns="target")

    target_df = ping_target(
        db=db,
        ad_id=ad_id,
        shop_id=shop_id,
        start_date=start_date,
        end_date=end_date,
        enum_to_value=enum_to_value,
    )

    df = creative_performance_df.merge(target_df, on=["adset_id", "account_id", "shop_id"])

    return df
