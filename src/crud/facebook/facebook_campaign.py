from sqlalchemy.orm import Session

from src.crud.base import CRUDBase
from src.models.facebook.facebook_campaign import FacebookCampaign
from src.schemas.facebook.facebook_campaign import FacebookCampaignCreate, FacebookCampaignUpdate


class CRUDFacebookCampaign(CRUDBase[FacebookCampaign, FacebookCampaignCreate, FacebookCampaignUpdate]):
    def get(self, db: Session, shop_id: int, account_id: str, campaign_id: str) -> FacebookCampaign | None:
        return db.query(self.model).get((shop_id, account_id, campaign_id))


fb_campaign = CRUDFacebookCampaign(FacebookCampaign)
