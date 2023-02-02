from sqlalchemy import BigInteger, Column, Date, ForeignKey, Numeric, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.database.base_class import Base


class FacebookDailyPerformance(Base):

    __tablename__ = "facebook_daily_performance"
    shop_id = Column(
        BigInteger, ForeignKey("shop.id"), nullable=False, primary_key=True
    )
    account_id = Column(String, primary_key=True)
    ad_id = Column(String, ForeignKey("facebook_ad.ad_id"), primary_key=True)
    date_start = Column(Date, primary_key=True)
    adset_id = Column(String)
    campaign_id = Column(String)
    spend = Column(Numeric)
    impressions = Column(BigInteger)
    clicks = Column(BigInteger)
    link_clicks = Column(BigInteger)
    landing_page_views = Column(BigInteger)
    add_to_cart = Column(BigInteger)
    initiate_checkout = Column(BigInteger)
    purchases = Column(BigInteger)
    actions = Column(JSONB().with_variant(sqlite.JSON, "sqlite"))
    action_values = Column(JSONB().with_variant(sqlite.JSON, "sqlite"))
    purchases_conversion_value = Column(Numeric)

    shop = relationship("Shop", back_populates="facebook_daily_performance")
    facebook_ad = relationship(
        "FacebookAd", back_populates="facebook_daily_performance"
    )
