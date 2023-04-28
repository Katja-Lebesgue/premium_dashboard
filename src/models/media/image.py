from sqlalchemy import (TIMESTAMP, BigInteger, Boolean, Column, ForeignKey,
                        Integer, String)
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import JSONB

from src.database.base_class import Base


class Image(Base):
    source_id = Column(String, primary_key=True)
    source = Column(String, primary_key=True)
    shop_id = Column(BigInteger, ForeignKey("shop.id"))
    width = Column(Integer)
    height = Column(Integer)
    created_at = Column(TIMESTAMP)
    url = Column(String)
    additional_data = Column(JSONB().with_variant(sqlite.JSON, "sqlite"))
    image_hash = Column(String)
    internally_saved = Column(Boolean)
    last_refreshed = Column(TIMESTAMP)
