from sqlalchemy import BigInteger, Column, Date, ForeignKey, String
from sqlalchemy.orm import relationship
from src.models.google.google_base import GoogleBase

from google.ads.googleads.v11.services.types.google_ads_service import GoogleAdsRow


class GoogleCampaign(GoogleBase):

    shop_id = Column(BigInteger, ForeignKey("shop.id"), primary_key=True)
    account_id = Column(BigInteger, primary_key=True)
    campaign_id = Column(BigInteger, primary_key=True)
    name = Column(String)
    type = Column(String)
    strategy = Column(String)
    experiment = Column(String)
    status = Column(String)
    start_date = Column(Date)

    shop = relationship("Shop")

    @classmethod
    def from_obj(cls, obj: GoogleAdsRow, account_id: int, shop_id: int) -> "GoogleCampaign":
        return cls(
            campaign_id=obj.campaign.id,
            name=obj.campaign.name,
            type=obj.campaign.advertising_channel_type.name,
            strategy=obj.campaign.bidding_strategy_type.name,
            experiment=obj.campaign.experiment_type.name,
            status=obj.campaign.status.name,
            start_date=obj.campaign.start_date,
            account_id=account_id,
            shop_id=shop_id,
        )
