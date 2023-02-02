from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship

from src.database.base_class import Base


class ShopifyCustomer(Base):
    id = Column(BigInteger().with_variant(sqlite.INTEGER, "sqlite"), primary_key=True, autoincrement=True)
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)
    gid = Column(String, unique=True)
    email = Column(String)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    account_state = Column(String)
    orders_count = Column(BigInteger)
    last_order_id = Column(BigInteger)
    first_order_id = Column(BigInteger)
    first_order_created_at = Column(DateTime(timezone=True))
    tags = Column(String)
    total_spent = Column(String)
    tax_exempt = Column(Boolean)
    currency = Column(String)
    accepts_marketing = Column(Boolean)
    default_country = Column(String)
    default_province = Column(String)
    default_country_code = Column(String)
    default_province_code = Column(String)

    shop = relationship("Shop")
