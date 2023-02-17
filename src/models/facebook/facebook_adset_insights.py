from sqlalchemy import BigInteger, Column, Date, ForeignKey, Numeric, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, synonym

from src.database.base_class import Base
from src.models.enums import EPlatform


class FacebookAdsetInsights(Base):
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False, primary_key=True)
    account_id = Column(String, primary_key=True)
    adset_id = Column(String, primary_key=True)
    date = Column(Date, primary_key=True)
    clicks = Column(BigInteger)
    link_clicks = Column(BigInteger)
    impressions = Column(BigInteger)
    spend = Column(Numeric)
    purchases = Column(BigInteger)
    purchases_conversion_value = Column(Numeric)
    shop = relationship("Shop", back_populates="facebook_adset_insights")

    platform = EPlatform.facebook
