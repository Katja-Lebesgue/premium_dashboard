from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship

from src.database.base_class import Base


class ShopifyProduct(Base):
    id = Column(BigInteger().with_variant(sqlite.INTEGER, "sqlite"), primary_key=True, autoincrement=True)
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)
    gid = Column(String, unique=True)
    title = Column(String)
    vendor = Column(String)
    handle = Column(String)
    product_type = Column(String)
    tags = Column(String)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    published_at = Column(DateTime(timezone=True))

    shop = relationship("Shop")
    product_variants = relationship("ShopifyProductVariant", cascade="all, delete-orphan")
