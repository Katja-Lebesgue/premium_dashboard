from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    ForeignKeyConstraint,
    Sequence,
)
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship

from src.database.base_class import Base


class ShopifyCustomer(Base):
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("shopify_customer_id_seq", start=-1, increment=-1),
        primary_key=True,
    )
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False, primary_key=True)
    gid = Column(String, unique=True)
    email = Column(String)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    account_state = Column(String)
    orders_count = Column(BigInteger)
    last_order_id = Column(BigInteger)
    first_order_id = Column(BigInteger)
    first_order_created_at = Column(DateTime(timezone=True))
    first_order_processed_at = Column(DateTime(timezone=True))
    tags = Column(String)
    total_spent = Column(String)
    tax_exempt = Column(Boolean)
    currency = Column(String)
    accepts_marketing = Column(Boolean)
    default_country = Column(String)
    default_province = Column(String)
    default_country_code = Column(String)
    default_province_code = Column(String)

    __table_args__ = (
        ForeignKeyConstraint(["first_order_id", "shop_id"], ["shopify_order.id", "shopify_order.shop_id"]),
    )

    shop = relationship("Shop", viewonly=True)
    first_order = relationship("ShopifyOrder", viewonly=True)
