from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.database.base_class import Base


class ShopifyLineItem(Base):
    id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, ForeignKey("shopify_order.id"), nullable=False)
    gid = Column(String, unique=True)
    title = Column(String)
    variant_id = Column(BigInteger)
    variant_title = Column(String)
    quantity = Column(BigInteger)
    sku = Column(String)
    product_id = Column(BigInteger)
    name = Column(String)
    price = Column(String)
    total_discount = Column(String)
    total_tax = Column(String)

    order = relationship("ShopifyOrder", back_populates="line_items")
    discount_allocations = relationship(
        "ShopifyDiscountAllocation", back_populates="line_item", cascade="all, delete-orphan"
    )
