from sqlalchemy import BigInteger, Column, ForeignKey, Integer, Sequence, String
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
    line_item_id = Column(BigInteger, ForeignKey("shopify_line_item.id"), nullable=False)
    amount = Column(String)
    discount_application_index = Column(Integer)

    line_item = relationship("ShopifyLineItem", back_populates="discount_allocations")
