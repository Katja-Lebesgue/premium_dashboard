from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Sequence, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from src.database.base_class import Base


class ShopLtvFilter(Base):
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )

    default = Column(Boolean, default=False)
    name = Column(String, nullable=False)
    params = Column(JSONB().with_variant(sqlite.JSON, "sqlite"))

    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)
    shop = relationship("Shop")
