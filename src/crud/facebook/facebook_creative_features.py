from datetime import date

from src.models import FacebookDailyPerformance
from sqlalchemy.orm import Session
from src.crud.base import CRUDBase
from src.models.enums.facebook.creative_features import CreativeType
from src.models.facebook.facebook_creative_features import FacebookCreativeFeatures
from src.schemas.facebook.facebook_creative_features import (
    FacebookCreativeFeaturesCreate,
    FacebookCreativeFeaturesUpdate,
)


class CRUDFacebookCreativeFeatures(
    CRUDBase[FacebookCreativeFeatures, FacebookCreativeFeaturesCreate, FacebookCreativeFeaturesUpdate]
):
    def get(self, db: Session, shop_id: int, account_id: str, ad_id: str) -> FacebookCreativeFeatures | None:
        return db.query(self.model).get((shop_id, account_id, ad_id))


fb_creative_features = CRUDFacebookCreativeFeatures(FacebookCreativeFeatures)
