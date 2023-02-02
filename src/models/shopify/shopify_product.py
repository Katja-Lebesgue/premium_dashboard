from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Enum
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship

from src.database.base_class import Base
from src.models.enums.shopify_product import ProductStatus


class ShopifyProduct(Base):
    id = Column(BigInteger().with_variant(sqlite.INTEGER, "sqlite"), primary_key=True)
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False, primary_key=True)
    gid = Column(String, unique=True)
    title = Column(String)
    description = Column(String)
    extracted_description = Column(String)
    vendor = Column(String)
    handle = Column(String)
    product_type = Column(String)
    tags = Column(String)
    status = Column(Enum(ProductStatus, native_enum=False))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    published_at = Column(DateTime(timezone=True))

    shop = relationship("Shop", viewonly=True)
    product_variants = relationship("ShopifyProductVariant", cascade="all, delete-orphan")
