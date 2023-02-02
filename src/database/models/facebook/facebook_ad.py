from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import JSONB
from src.database.base_class import Base
from sqlalchemy.orm import relationship


class FacebookAd(Base):

    __tablename__ = "facebook_ad"
    shop_id = Column(BigInteger, ForeignKey("shop.id"), primary_key=True)
    account_id = Column(String, primary_key=True)
    ad_id = Column(String, primary_key=True)
    adset_id = Column(String, ForeignKey("facebook_adset.adset_id"))
    campaign_id = Column(String)
    creative_id = Column(String)
    name = Column(String)
    status = Column(String)
    created_time = Column(DateTime(timezone=True))
    body_text = Column(String)
    creative = Column(JSONB().with_variant(sqlite.JSON, "sqlite"))

    facebook_daily_performance = relationship(
        "FacebookDailyPerformance", back_populates="facebook_ad"
    )
