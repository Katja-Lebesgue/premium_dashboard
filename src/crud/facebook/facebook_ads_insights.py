from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from sqlalchemy.sql.expression import literal
from src.crud.base import CRUDBase
from src.models.facebook.facebook_ads_insights import FacebookAdsInsights
from src.schemas.facebook.facebook_ads_insights import FacebookAdsInsightsCreate, FacebookAdsInsightsUpdate


class CRUDFacebookAdsInsights(CRUDBase[FacebookAdsInsights, FacebookAdsInsightsCreate, FacebookAdsInsightsUpdate]):
    def get(self, db: Session, shop_id: int, facebook_account_id: str, date: date) -> FacebookAdsInsights | None:
        return db.query(self.model).get((shop_id, facebook_account_id, date))


fb_ads_insights = CRUDFacebookAdsInsights(FacebookAdsInsights)
