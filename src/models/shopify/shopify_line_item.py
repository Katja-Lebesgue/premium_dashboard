from sqlalchemy import BigInteger, Column, ForeignKey, String, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from src.database.base_class import Base


class ShopifyLineItem(Base):
    id = Column(BigInteger, primary_key=True)
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False, primary_key=True)
    order_id = Column(BigInteger, nullable=False)
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

    __table_args__ = (
        ForeignKeyConstraint(["order_id", "shop_id"], ["shopify_order.id", "shopify_order.shop_id"]),
    )

    order = relationship("ShopifyOrder", back_populates="line_items", viewonly=True)
    discount_allocations = relationship(
        "ShopifyDiscountAllocation", back_populates="line_item", cascade="all, delete-orphan"
    )
