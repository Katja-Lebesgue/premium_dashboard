from datetime import date, datetime

import pandas as pd
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src import crud, utils
from src.database.session import SessionLocal
from src.feature_extractors import *
from src.models import *
from src.pingers.ping_facebook_creative_features import ping_facebook_creative


def ping_facebook_creative_target_and_performance(
    db: Session,
    ad_id: str | list[str] = None,
    shop_id: str | list[str] = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
    monthly: bool = True,
    cast_to_date: bool = True,
    enum_to_value: bool = False,
) -> pd.DataFrame:
    if all([x is None for x in [ad_id, shop_id, start_date]]):
        print("No filters in ping_facebook_creative_and_performance!")
        return None

    creative = ping_facebook_creative(
        db=db,
        shop_id=shop_id,
        ad_id=ad_id,
        start_date=start_date,
        end_date=end_date,
        enum_to_value=enum_to_value,
    )

    creative = creative.drop(columns=["target"])

    if len(creative) == 0:
        return creative

    target_df = ping_target(
        db=db,
        ad_id=ad_id,
        shop_id=shop_id,
        start_date=start_date,
        end_date=end_date,
        enum_to_value=enum_to_value,
    )

    if len(target_df) == 0:
        return target_df

    performance = crud.fb_daily_performance.get_performance(
        db=db,
        shop_id=shop_id,
        ad_id=ad_id,
        start_date=start_date,
        end_date=end_date,
        monthly=monthly,
        cast_to_date=cast_to_date,
    )

    if len(performance) == 0:
        return creative

    df = creative.merge(target, on=["ad_id", "account_id", "shop_id"]).merge(performance)

    return df
