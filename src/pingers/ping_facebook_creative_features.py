from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from src.models import FacebookCreativeFeatures, FacebookDailyPerformance
from src.utils import *


def ping_facebook_creative(
    db: Session,
    shop_id: int | list[int],
    ad_id: str | list[str] = None,
    start_date: date | str | None = None,
    end_date: date | str = date.today(),
    enum_to_value: bool = False,
) -> pd.DataFrame:
    if all([x is None for x in [ad_id, shop_id, start_date]]):
        raise Exception("No filters!")

    query = db.query(FacebookCreativeFeatures)

    if start_date is not None:
        query = query.join(
            FacebookDailyPerformance,
            (FacebookCreativeFeatures.ad_id == FacebookDailyPerformance.ad_id)
            & (FacebookCreativeFeatures.shop_id == FacebookDailyPerformance.shop_id)
            & (FacebookCreativeFeatures.account_id == FacebookDailyPerformance.account_id),
        ).filter(FacebookDailyPerformance.date_start.between(start_date, end_date))

    filters = []

    if ad_id is not None:
        ad_id = element_to_list(ad_id)
        filters.append(FacebookCreativeFeatures.ad_id.in_(ad_id))
    if shop_id is not None:
        shop_id = element_to_list(shop_id)
        filters.append(FacebookCreativeFeatures.shop_id.in_(shop_id))
    if len(filters):
        query = query.filter(*filters)

    query = query.distinct(FacebookCreativeFeatures.ad_id, FacebookCreativeFeatures.shop_id)

    df = read_query_into_df(db=db, query=query)

    if enum_to_value:
        df = df.applymap(convert_enum_to_its_value)

    df.discount_list = df.discount_list.apply(lambda x: x if len(x) else [0])

    return df
