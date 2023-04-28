from sqlalchemy import BigInteger, Column, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship

from src.models.google.google_base import GoogleBase


class GoogleDailyPerformance(GoogleBase):
    shop_id = Column(BigInteger, ForeignKey("shop.id"), primary_key=True)
    account_id = Column(BigInteger, primary_key=True)
    ad_id = Column(BigInteger, primary_key=True)
    date_start = Column(Date, primary_key=True)
    adgroup_id = Column(BigInteger, primary_key=True)
    campaign_id = Column(BigInteger, primary_key=True)
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
