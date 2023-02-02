from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.database.base_class import Base
from src.database.models.enums.facebook.adset import Target
from sqlalchemy.ext.hybrid import hybrid_property


class FacebookAdset(Base):
    __tablename__ = "facebook_adset"
    shop_id = Column(BigInteger, ForeignKey("shop.id"), primary_key=True)
    account_id = Column(String, primary_key=True)
    adset_id = Column(String, primary_key=True)
    campaign_id = Column(String)
    name = Column(String)
    optimization_goal = Column(String)
    targeting = Column("targeting", JSONB().with_variant(sqlite.JSON, "sqlite"))
    status = Column(String)
    created_time = Column(DateTime(timezone=True))
    target = Column(Enum(Target, native_enum=False))

    shop = relationship("Shop", back_populates="facebook_ad_sets")

    @hybrid_property
    def geo_locations(self) -> str:
        return self.targeting["geo_locations"]

    @hybrid_property
    def country(self) -> str:
        return self.targeting["geo_locations"]["country"]
