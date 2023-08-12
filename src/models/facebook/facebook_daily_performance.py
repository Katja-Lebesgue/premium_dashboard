from sqlalchemy import BigInteger, Column, Date, ForeignKey, Numeric, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, synonym

from src.database.base_class import Base


class FacebookDailyPerformance(Base):
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False, primary_key=True)
    account_id = Column(String, primary_key=True)
    ad_id = Column(String, primary_key=True)
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

    # synonyms
    adgroup_id_ = synonym("adset_id")
    clicks_ = synonym("link_clicks")
    purch_ = synonym("purchases")
    purch_value_ = synonym("purchases_conversion_value")

    shop = relationship("Shop", back_populates="facebook_daily_performance")
