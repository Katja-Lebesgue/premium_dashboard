from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String
from sqlalchemy.orm import relationship
from src.database.models.google.google_base import GoogleBase

from google.ads.googleads.v10.services.types.google_ads_service import GoogleAdsRow


class GoogleAd(GoogleBase):

    shop_id = Column(BigInteger, ForeignKey("shop.id"), primary_key=True)
    account_id = Column(BigInteger, primary_key=True)
    ad_id = Column(BigInteger, primary_key=True)
    adgroup_id = Column(BigInteger)
    campaign_id = Column(BigInteger)
    name = Column(String)
    added_by_google = Column(Boolean)
    type = Column(String)
    approval_status = Column(String)
    review_status = Column(String)
    status = Column(String)
    final_urls = Column(String)

    shop = relationship("Shop")

    @classmethod
    def from_obj(cls, obj: GoogleAdsRow, account_id: int, shop_id: int) -> "GoogleAd":
        return cls(
            ad_id=obj.ad_group_ad.ad.id,
            adgroup_id=obj.ad_group.id,
            campaign_id=obj.campaign.id,
            name=obj.ad_group_ad.ad.name,
            added_by_google=obj.ad_group_ad.ad.added_by_google_ads,
            type=obj.ad_group_ad.ad.type_.name,
            approval_status=obj.ad_group_ad.policy_summary.approval_status.name,
            review_status=obj.ad_group_ad.policy_summary.review_status.name,
            status=obj.ad_group_ad.status.name,
            final_urls=",".join(obj.ad_group_ad.ad.final_urls),
            account_id=account_id,
            shop_id=shop_id,
        )
