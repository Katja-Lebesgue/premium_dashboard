from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from src import crud
from src.feature_extractors import *
from src.models import *
from src.pingers.ping_facebook_creative_features import ping_facebook_creative
from src.utils import *


def ping_facebook_creative_and_performance(
    db: Session,
    ad_id: str | list[str] = None,
    shop_id: str | list[str] = None,
    start_date: date | str | None = None,
    end_date: date | str = date.today(),
    period: Period = Period.year_month,
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

    if len(creative) == 0:
        return creative

    performance = crud.fb_daily_performance.get_performance(
        db=db,
        shop_id=shop_id,
        ad_id=ad_id,
        start_date=start_date,
        end_date=end_date,
        period=period,
        cast_to_date=cast_to_date,
    )

    if len(performance) == 0:
        return creative

    df = creative.merge(performance)

    return df
