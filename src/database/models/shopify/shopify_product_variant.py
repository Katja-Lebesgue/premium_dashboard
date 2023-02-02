from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship

from src.database.base_class import Base


class ShopifyProductVariant(Base):
    id = Column(BigInteger().with_variant(sqlite.INTEGER, "sqlite"), primary_key=True, autoincrement=True)
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("shopify_product.id"), nullable=False)
    gid = Column(String, unique=True)
    title = Column(String)
    sku = Column(String)
    price = Column(String)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    taxable = Column(Boolean)
    requires_shipping = Column(Boolean)
    inventory_item_id = Column(BigInteger)

    shop = relationship("Shop")
    product = relationship("ShopifyProduct", back_populates="product_variants")
