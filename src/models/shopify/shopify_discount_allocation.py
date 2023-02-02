from sqlalchemy import BigInteger, Column, ForeignKey, Integer, Sequence, String, ForeignKeyConstraint
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship

from src.database.base_class import Base


class ShopifyDiscountAllocation(Base):
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)
    line_item_id = Column(BigInteger, nullable=False)
    amount = Column(String)
    discount_application_index = Column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(
            ["line_item_id", "shop_id"], ["shopify_line_item.id", "shopify_line_item.shop_id"]
        ),
    )

    line_item = relationship("ShopifyLineItem", back_populates="discount_allocations", viewonly=True)
