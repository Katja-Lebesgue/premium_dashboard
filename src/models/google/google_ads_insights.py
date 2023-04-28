from sqlalchemy import BigInteger, Column, Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship, synonym

from src.models.enums import EPlatform
from src.models.google.google_base import GoogleBase


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
    revenue = synonym("total_purchase_value")

    shop = relationship("Shop", back_populates="google_ads_insights")

    platform = EPlatform.google
