from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    ForeignKeyConstraint,
)
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.orm import relationship

from src.database.base_class import Base


class CustomerFirstOrderProperties(Base):
    __table_args__ = (UniqueConstraint("shop_id", "customer_id"),)
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False, primary_key=True)
    customer_id = Column(BigInteger, nullable=False, primary_key=True)
    order_id = Column(BigInteger, nullable=False, primary_key=True)
    order_processed_at = Column(DateTime)
    order_product_ids = Column(
        postgresql.ARRAY(BigInteger).with_variant(sqlite.JSON, "sqlite"), server_default="{}"
    )
    order_utms = Column(postgresql.JSONB(none_as_null=True).with_variant(sqlite.JSON, "sqlite"))
    order_channel = Column(String)
    order_discount_codes = Column(
        postgresql.ARRAY(String).with_variant(sqlite.JSON, "sqlite"), server_default="{}"
    )
    order_discount_titles = Column(
        postgresql.ARRAY(String).with_variant(sqlite.JSON, "sqlite"), server_default="{}"
    )
    customer_default_country_name = Column(String)
    customer_default_province_name = Column(String)

    __table_args__ = (
        ForeignKeyConstraint(["customer_id", "shop_id"], ["shopify_customer.id", "shopify_customer.shop_id"]),
        ForeignKeyConstraint(["order_id", "shop_id"], ["shopify_order.id", "shopify_order.shop_id"]),
    )

    shop = relationship("Shop")
    customer = relationship("ShopifyCustomer")
    order = relationship("ShopifyOrder")

    def set_shop(self, shop):
        self.shop_id = shop.id
        self.shop = shop

    def set_customer(self, customer):
        self.customer_id = customer.id
        self.customer = customer

    def set_order(self, order):
        self.order_id = order.id
        self.order = order
