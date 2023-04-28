from sqlalchemy import (JSON, BigInteger, Boolean, Column, DateTime,
                        ForeignKey, String)
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.database.base_class import Base

UTM_SOURCE_KEY = "source"
UTM_MEDIUM_KEY = "medium"
UTM_CAMPAIGN_KEY = "campaign"
UTM_TERM_KEY = "term"
UTM_CONTENT_KEY = "content"
UTM_PARAMETER_KEYS = [UTM_SOURCE_KEY, UTM_MEDIUM_KEY, UTM_CAMPAIGN_KEY, UTM_TERM_KEY, UTM_CONTENT_KEY]


class ShopifyOrder(Base):
    id = Column(BigInteger().with_variant(sqlite.INTEGER, "sqlite"), primary_key=True)
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False, primary_key=True)
    gid = Column(String, unique=True)
    email = Column(String)
    created_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))
    processed_at = Column(DateTime(timezone=True))
    test = Column(Boolean)
    total_price = Column(String)
    total_price_usd = Column(String)
    subtotal_price = Column(String)
    total_tax = Column(String)
    total_discounts = Column(String)
    total_line_items_price = Column(String)
    total_shipping_price = Column(String)
    currency = Column(String)
    presentment_currency = Column(String)
    taxes_included = Column(Boolean)
    confirmed = Column(Boolean)
    buyer_accepts_marketing = Column(Boolean)
    referring_site = Column(String)
    landing_site = Column(String)
    cancel_reason = Column(String)
    user_id = Column(BigInteger)
    customer_id = Column(BigInteger)
    app_id = Column(BigInteger)
    utm_parameters = Column(JSONB(none_as_null=True).with_variant(JSON(), "sqlite"), nullable=True)
    status = Column(String)
    billing = Column(JSON)

    shop = relationship("Shop", viewonly=True)
