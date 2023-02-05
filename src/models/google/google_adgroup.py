from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship
from src.models.google.google_base import GoogleBase

from google.ads.googleads.v11.services.types.google_ads_service import GoogleAdsRow


class GoogleAdgroup(GoogleBase):

    shop_id = Column(BigInteger, ForeignKey("shop.id"), primary_key=True)
    account_id = Column(BigInteger, primary_key=True)
    adgroup_id = Column(BigInteger, primary_key=True)
    campaign_id = Column(BigInteger)
    name = Column(String)
    status = Column(String)
    type = Column(String)

    shop = relationship("Shop")

    @classmethod
    def from_obj(cls, obj: GoogleAdsRow, account_id: int, shop_id: int) -> "GoogleAdgroup":
        return cls(
            adgroup_id=obj.ad_group.id,
            campaign_id=obj.campaign.id,
            name=obj.ad_group.name,
            status=obj.ad_group.status.name,
            type=obj.ad_group.type_.name,
            account_id=account_id,
            shop_id=shop_id,
        )
