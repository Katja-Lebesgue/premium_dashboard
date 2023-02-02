from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Sequence, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship

from src.database.base_class import Base


class ShopBilling(Base):
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)
    billing_plan = Column(String)
    amount = Column(String)
    updated_at = Column(DateTime)
    active = Column(Boolean, default=False)

    shop = relationship("Shop")
