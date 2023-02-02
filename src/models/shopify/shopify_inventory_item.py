from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship

from src.database.base_class import Base


class ShopifyInventoryItem(Base):
    id = Column(BigInteger().with_variant(sqlite.INTEGER, "sqlite"), primary_key=True)
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False, primary_key=True)
    gid = Column(String)
    cost = Column(String)
    sku = Column(String)
    tracked = Column(Boolean)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))

    shop = relationship("Shop", viewonly=True)
