from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.database.base_class import Base


class Insight(Base):
    id = Column(BigInteger().with_variant(sqlite.INTEGER, "sqlite"), primary_key=True)
    variant = Column(String)
    title = Column(String)
    body = Column(String)
    created_at = Column(DateTime(timezone=True))
    properties = Column(JSONB().with_variant(sqlite.JSON, "sqlite"))
    shop_id = Column(BigInteger, ForeignKey("shop.id"))
    time_interval = Column(String)
    sign = Column(String)
    dismiss = Column(Boolean)
    source = Column(String)

    shop = relationship("Shop")
