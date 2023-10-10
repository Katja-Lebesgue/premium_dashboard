import pandas as pd
from sqlalchemy import and_

from src import crud
from src.database.session import *
from src.models import *
from src.utils import *


def ping_raw_creative_and_target(session=SessionLocal(), ad_id: str = None, shop_id: str = None):
    creative_query = crud.fb_ad.query_raw_creative_data(session=session, ad_id=ad_id, shop_id=shop_id)
    target_query = crud.fb_adset.query_target(session=session, shop_id=shop_id).subquery()

    query = creative_query.join(
        target_query,
        and_(
            FacebookAd.shop_id == target_query.c.shop_id,
            FacebookAd.adset_id == target_query.c.adset_id,
            FacebookAd.account_id == target_query.c.account_id,
        ),
    ).add_columns(target_query)

    df = read_query_into_df(db=db, query=query)

    return df
