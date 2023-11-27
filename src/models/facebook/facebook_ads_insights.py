from sqlalchemy import BigInteger, Column, Date, ForeignKey, Numeric, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, synonym

from src.database.base_class import Base
from src.models.enums import EPlatform


class FacebookAdsInsights(Base):
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False, primary_key=True)
    facebook_account_id = Column(String, primary_key=True)
    date = Column(Date, primary_key=True)
    clicks = Column(BigInteger)
    link_clicks = Column(BigInteger)
    outbound_clicks = Column(BigInteger)
    cpc = Column(Numeric)
    cpm = Column(Numeric)
    ctr = Column(Numeric)
    impressions = Column(BigInteger)
    reach = Column(BigInteger)
    spend = Column(Numeric)
    purchases = Column(BigInteger)
    oned_view_purchases = Column(BigInteger)
    oned_click_purchases = Column(BigInteger)
    purchases_conversion_value = Column(Numeric)
    actions = Column(JSONB().with_variant(sqlite.JSON, "sqlite"))
    action_values = Column(JSONB().with_variant(sqlite.JSON, "sqlite"))
    revenue = synonym("purchases_conversion_value")
    shop = relationship("Shop", back_populates="facebook_ads_insights")

    # synonyms
    clicks_ = synonym("link_clicks")
    purch_ = synonym("purchases")
    purch_value_ = synonym("purchases_conversion_value")

    platform = EPlatform.facebook
