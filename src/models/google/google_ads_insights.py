from sqlalchemy import BigInteger, Column, Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from src.models.google.google_base import GoogleBase

from google.ads.googleads.v11.services.types.google_ads_service import GoogleAdsRow


class GoogleAdsInsights(GoogleBase):

    shop_id = Column(BigInteger, ForeignKey("shop.id"), primary_key=True)
    google_account_id = Column(BigInteger, primary_key=True)
    date = Column(Date, primary_key=True)
    clicks = Column(BigInteger)
    impressions = Column(BigInteger)
    cost_micros = Column(BigInteger)
    conversions = Column(Numeric)
    total_conversion_value = Column(Numeric)
    conversions_purchase = Column(Numeric)
    total_purchase_value = Column(Numeric)
    spend = Column(Numeric)

    shop = relationship("Shop", back_populates="google_ads_insights")

    @classmethod
    def from_obj(cls, obj: GoogleAdsRow, account_id: int, shop_id: int) -> "GoogleAdsInsights":
        return cls(
            date=obj.segments.date,
            clicks=obj.metrics.clicks,
            impressions=obj.metrics.impressions,
            cost_micros=obj.metrics.cost_micros,
            conversions=obj.metrics.conversions,
            total_conversion_value=obj.metrics.conversions_value,
            spend=obj.metrics.cost_micros / 10**6,
            google_account_id=account_id,
            shop_id=shop_id,
        )
