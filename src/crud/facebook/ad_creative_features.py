from datetime import date
from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Query, Session

from src.crud.base import CRUDBase
from src.models import FacebookDailyPerformance
from src.models.facebook.ad_creative_features import AdCreativeFeatures
from src.schemas.facebook.ad_creative_features import (
    AdCreativeFeaturesCreate, AdCreativeFeaturesUpdate)
from src.utils.common import element_to_list


class CRUDAdCreativeFeatures(CRUDBase[AdCreativeFeatures, AdCreativeFeaturesCreate, AdCreativeFeaturesUpdate]):
    def get(self, db: Session, shop_id: int, account_id: str, ad_id: str) -> AdCreativeFeatures | None:
        return db.query(self.model).get((shop_id, account_id, ad_id))

    def get_features_by_shop_id(self, db: Session, shop_id: int) -> List[str]:
        ad_creative_features = AdCreativeFeatures
        result = db.query(ad_creative_features.feature).filter(ad_creative_features.shop_id == shop_id).distinct()
        return result

    def get_distinct_features_by_shop_id(self, db: Session, shop_id: int) -> list[str]:
        query = db.query(AdCreativeFeatures.feature).filter(AdCreativeFeatures.shop_id == shop_id).distinct()
        features = [q[0] for q in query]
        return features

    def query_creative(
        self,
        db: Session,
        shop_id: int | list[int],
        ad_id: str | list[str] = None,
        start_date: str = None,
        end_date: str = date.today().strftime("%Y-%m-%d"),
    ) -> Query:

        query = db.query(AdCreativeFeatures)

        if shop_id is not None:
            shop_id = element_to_list(shop_id)
            query = query.filter(AdCreativeFeatures.shop_id.in_(shop_id))

        if ad_id is not None:
            ad_id = element_to_list(ad_id)
            query = query.filter(AdCreativeFeatures.ad_id.in_(ad_id))

        if start_date is not None:

            query = query.join(
                FacebookDailyPerformance,
                and_(
                    AdCreativeFeatures.shop_id == FacebookDailyPerformance.shop_id,
                    AdCreativeFeatures.account_id == FacebookDailyPerformance.account_id,
                    AdCreativeFeatures.ad_id == FacebookDailyPerformance.ad_id,
                ),
            )
            query = query.filter(FacebookDailyPerformance.date_start.between(start_date, end_date))

        query = query.distinct()

        return query


crud_ad_creative_features = CRUDAdCreativeFeatures(AdCreativeFeatures)
