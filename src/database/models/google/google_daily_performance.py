from sqlalchemy import BigInteger, Column, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship
from src.database.models.google.google_base import GoogleBase

from google.ads.googleads.v10.services.types.google_ads_service import GoogleAdsRow


class GoogleDailyPerformance(GoogleBase):
    shop_id = Column(BigInteger, ForeignKey("shop.id"), primary_key=True)
    account_id = Column(BigInteger, primary_key=True)
    ad_id = Column(BigInteger, primary_key=True)
    date_start = Column(Date, primary_key=True)
    adgroup_id = Column(BigInteger)
    campaign_id = Column(BigInteger)
    type = Column(String)
    impressions = Column(BigInteger)
    clicks = Column(BigInteger)
    conversions_all = Column(Numeric)
    conversions_value_all = Column(Numeric)
    conversions = Column(Numeric)
    conversions_value = Column(Numeric)
    spend = Column(Numeric)
    conversions_purchase = Column(Numeric)
    conversions_value_purchase = Column(Numeric)

    shop = relationship("Shop")

    @classmethod
    def from_obj(
        cls, obj: GoogleAdsRow, account_id: int, shop_id: int
    ) -> "GoogleDailyPerformance":
        return cls(
            ad_id=obj.ad_group_ad.ad.id,
            adgroup_id=obj.ad_group.id,
            campaign_id=obj.campaign.id,
            date_start=obj.segments.date,
            type=obj.campaign.advertising_channel_type.name,
            impressions=obj.metrics.impressions,
            clicks=obj.metrics.clicks,
            conversions_all=obj.metrics.all_conversions,
            conversions_value_all=obj.metrics.all_conversions_value,
            conversions=obj.metrics.conversions,
            conversions_value=obj.metrics.conversions_value,
            spend=obj.metrics.cost_micros / 10**6,
            account_id=account_id,
            shop_id=shop_id,
        )
