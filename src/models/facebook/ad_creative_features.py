from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.database.base_class import Base


class AdCreativeFeatures(Base):

    shop_id = Column(BigInteger, ForeignKey("shop.id"), primary_key=True)
    account_id = Column(String, primary_key=True)
    ad_id = Column(String, primary_key=True)
    creative_id = Column(String)
    feature = Column(String, primary_key=True)
    value = Column(JSONB(none_as_null=True).with_variant(sqlite.JSON, "sqlite"))

    shop = relationship("Shop", back_populates="ad_creative_features")
