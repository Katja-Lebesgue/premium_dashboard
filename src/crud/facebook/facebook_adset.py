from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

from src.crud.base import CRUDBase
from src.models.facebook.facebook_adset import FacebookAdset
from src.schemas.facebook.facebook_adset import (FacebookAdsetCreate,
                                                 FacebookAdsetUpdate)
from src.utils import element_to_list


class CRUDFacebookAdset(CRUDBase[FacebookAdset, FacebookAdsetCreate, FacebookAdsetUpdate]):
    def get(self, db: Session, shop_id: int, account_id: str, adset_id: str) -> FacebookAdset | None:
        return db.query(self.model).get((shop_id, account_id, adset_id))

    def query_target_features(
        self,
        db: Session,
        adset_id: str | list[str] | None = None,
        account_id: str | list[str] | None = None,
        shop_id: int | list[int] | None = None,
    ) -> Query:
        query = db.query(
            FacebookAdset.adset_id,
            FacebookAdset.account_id,
            FacebookAdset.shop_id,
            FacebookAdset.target,
            FacebookAdset.targeting,
            FacebookAdset.targeting["geo_locations"]["countries"].label("countries"),
            FacebookAdset.targeting["age_max"].label("age_max"),
            FacebookAdset.targeting["age_min"].label("age_min"),
            FacebookAdset.targeting["custom_audiences"].label("custom_audiences"),
            FacebookAdset.targeting["flexible_specs"].label("flexible_specs"),
        )

        if shop_id is not None:
            shop_id = element_to_list(shop_id)
            query = query.filter(FacebookAdset.shop_id.in_(shop_id))

        if account_id is not None:
            account_id = element_to_list(account_id)
            query = query.filter(FacebookAdset.account_id.in_(account_id))

        if adset_id is not None:
            adset_id = element_to_list(adset_id)
            query = query.filter(FacebookAdset.adset_id.in_(adset_id))

        query = query.distinct()

        return query


fb_adset = CRUDFacebookAdset(FacebookAdset)
