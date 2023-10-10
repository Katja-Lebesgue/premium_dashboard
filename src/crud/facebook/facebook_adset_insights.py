from datetime import date

import numpy as np
import pandas as pd
from loguru import logger
from sqlalchemy import and_, func, insert
from sqlalchemy.orm import Query, Session
from sqlalchemy.sql.expression import literal
from tqdm import tqdm

from src.crud.base import CRUDBase
from src.crud.currency_exchange_rate import currency_exchange_rate as crud_currency_exchange_rate
from src.models import *
from src.schemas.facebook.facebook_adset_insights import (
    FacebookAdsetInsightsCreate,
    FacebookAdsetInsightsUpdate,
)
from src.utils import element_to_list, read_query_into_df


class CRUDFacebookAdsetInsights(
    CRUDBase[FacebookAdsetInsights, FacebookAdsetInsightsCreate, FacebookAdsetInsightsUpdate]
):
    def get(
        self, db: Session, shop_id: int, facebook_account_id: str, date: date
    ) -> FacebookAdsetInsights | None:
        return db.query(self.model).get((shop_id, facebook_account_id, date))

    def rebuild_table(self, db: Session, chunk_size: int = 5):
        logger.debug(self.model.__table__.name)
        truncate_query = f"truncate table {self.model.__table__.name}"
        db.execute(truncate_query)

        fdp = FacebookDailyPerformance
        fas = FacebookAdset
        fai = self.model
        shop_ids_query = db.query(fas.shop_id).distinct()
        shop_ids = read_query_into_df(db=db, query=shop_ids_query)["shop_id"].tolist()

        group_cols = [
            fdp.shop_id,
            fdp.account_id,
            fdp.adset_id,
            fdp.date_start,
        ]

        feat_cols = [
            func.sum(fdp.spend),
            func.sum(fdp.impressions),
            func.sum(fdp.link_clicks),
            func.sum(fdp.clicks),
            func.sum(fdp.purchases),
            func.sum(fdp.purchases_conversion_value),
        ]

        adset_insights_cols = (
            fai.shop_id,
            fai.account_id,
            fai.adset_id,
            fai.date,
            fai.spend,
            fai.impressions,
            fai.link_clicks,
            fai.clicks,
            fai.purchases,
            fai.purchases_conversion_value,
        )

        for start_idx in tqdm(range(0, len(shop_ids) + 1, chunk_size)):
            chunk = shop_ids[start_idx : start_idx + chunk_size]
            q = (
                db.query(*(group_cols + feat_cols))
                .join(
                    fas,
                    (fdp.shop_id == fas.shop_id)
                    & (fdp.account_id == fas.account_id)
                    & (fdp.adset_id == fas.adset_id),
                )
                .filter(fdp.shop_id.in_(chunk))
                .group_by(*group_cols)
            )
            ins = insert(FacebookAdsetInsights).from_select(adset_insights_cols, q)
            print(ins)
            break
            # db.execute(ins)

    def query_budget_split_by_target(
        self,
        db: Session,
        shop_id: int | list[int] = None,
        start_date: date | str | None = None,
        end_date: date | str = date.today(),
    ) -> Query:
        currency_subquery = crud_currency_exchange_rate.query_current_rates(db=db).subquery()

        group_columns = [
            self.model.shop_id,
            self.model.account_id,
            self.model.adset_id,
            FacebookAdset.target,
        ]

        performance_columns = [
            func.sum(self.model.spend).label("spend"),
        ]

        columns = group_columns + performance_columns

        main_query = db.query(*columns).join(
            FacebookAdset,
            (self.model.shop_id == FacebookAdset.shop_id)
            & (self.model.account_id == FacebookAdset.account_id)
            & (self.model.adset_id == FacebookAdset.adset_id),
        )

        if shop_id is not None:
            shop_id = element_to_list(shop_id)
            main_query = main_query.filter(self.model.shop_id.in_(shop_id))

        if start_date is not None:
            main_query = main_query.filter(
                self.model.date_start >= start_date,
                self.model.date_start <= end_date,
            )

        main_query = main_query.group_by(*group_columns).subquery()

        query = db.query(
            main_query.c.shop_id,
            main_query.c.target,
            func.sum(main_query.c.spend / currency_subquery.c.rate_from_usd).label("spend_USD"),
        )

        query = query.join(
            FacebookAdAccount,
            (main_query.c.account_id == FacebookAdAccount.facebook_id)
            & (main_query.c.shop_id == FacebookAdAccount.shop_id),
        )

        query = query.join(currency_subquery, FacebookAdAccount.currency == currency_subquery.c.code)

        query = query.group_by(main_query.c.shop_id, main_query.c.target)

        return query


fb_adset_insights = CRUDFacebookAdsetInsights(FacebookAdsetInsights)
