from sqlalchemy import BigInteger, Column, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship
from src.database.base_class import Base


class TikTokAdsInsights(Base):
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False, primary_key=True)
    tiktok_account_id = Column(String, primary_key=True)
    date = Column(Date, primary_key=True)
    currency = Column(String(length=3))

    clicks = Column(BigInteger)
    impressions = Column(BigInteger)
    add_to_cart = Column(BigInteger)
    initiate_checkout = Column(BigInteger)
    complete_payment = Column(BigInteger)
    total_complete_payment_rate = Column(Numeric)
    spend = Column(Numeric)

    shop = relationship("Shop", back_populates="tiktok_ads_insights")
