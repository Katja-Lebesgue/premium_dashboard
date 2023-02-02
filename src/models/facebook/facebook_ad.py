from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import JSONB

from src.database.base_class import Base


class FacebookAd(Base):
    shop_id = Column(BigInteger, ForeignKey("shop.id"), primary_key=True)
    account_id = Column(String, primary_key=True)
    ad_id = Column(String, primary_key=True)
    adset_id = Column(String)
    campaign_id = Column(String)
    creative_id = Column(String)
    name = Column(String)
    status = Column(String)
    created_time = Column(DateTime(timezone=True))
    body_text = Column(String)
    ad_language = Column(String)
    creative = Column(JSONB().with_variant(sqlite.JSON, "sqlite"))
