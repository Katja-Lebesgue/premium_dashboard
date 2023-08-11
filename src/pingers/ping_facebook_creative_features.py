from datetime import date

import pandas as pd
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src import crud
from src.database.session import SessionLocal
from src.models import FacebookCreativeFeatures, FacebookDailyPerformance, AdCreativeFeatures
from src.pingers.ping_crm import ping_crm
from src.s3 import *
from src.utils import *


def ping_facebook_creative(
    db: Session,
    shop_id: int | list[int],
    ad_id: str | list[str] = None,
    start_date: str = None,
    end_date: str = date.today().strftime("%Y-%m-%d"),
) -> pd.DataFrame:
    if all([x is None for x in [ad_id, shop_id, start_date]]):
        raise Exception("No filters!")

    query = db.query(
        FacebookCreativeFeatures.shop_id,
        FacebookCreativeFeatures.account_id,
        FacebookCreativeFeatures.ad_id,
        FacebookCreativeFeatures.creative_type,
        FacebookCreativeFeatures.title,
        FacebookCreativeFeatures.primary,
        FacebookCreativeFeatures.description,
        FacebookCreativeFeatures.cta,
        FacebookCreativeFeatures.discount,
        FacebookCreativeFeatures.emoji,
        FacebookCreativeFeatures.emoji_list,
        FacebookCreativeFeatures.free_shipping,
        FacebookCreativeFeatures.fact_words,
        FacebookCreativeFeatures.hashtag,
        FacebookCreativeFeatures.link,
        FacebookCreativeFeatures.percentage,
        FacebookCreativeFeatures.price,
        FacebookCreativeFeatures.starts_with_question,
        FacebookCreativeFeatures.urgency,
        FacebookCreativeFeatures.user_addressing,
        FacebookCreativeFeatures.weasel_words,
        FacebookCreativeFeatures.target,
    )

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

    df = pd.read_sql(query.statement, db.bind)

    return df
