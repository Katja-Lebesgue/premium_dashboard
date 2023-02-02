from sqlalchemy import BigInteger, Column, ForeignKey, Integer, Sequence, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship

from src.database.base_class import Base


class ShopifyDiscountApplication(Base):
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)
    order_id = Column(BigInteger, ForeignKey("shopify_order.id"), nullable=False)
    index = Column(Integer)
    type = Column(String)
    title = Column(String)
    description = Column(String)
    code = Column(String)
    value = Column(String)
    value_type = Column(String)
    allocation_method = Column(String)
    target_selection = Column(String)
    target_type = Column(String)

    shop = relationship("Shop")
    order = relationship("ShopifyOrder", back_populates="discount_applications")
