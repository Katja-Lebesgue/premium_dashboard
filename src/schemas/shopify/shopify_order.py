from datetime import datetime

from pydantic import BaseModel


class ShopifyOrderBase(BaseModel):
    id: int
    shop_id: int
    gid: str
    email: str | None
    created_at: datetime | None
    cancelled_at: datetime | None
    updated_at: datetime | None
    closed_at: datetime | None
    processed_at: datetime | None
    test: bool
    total_price: str
    total_price_usd: str | None
    subtotal_price: str | None
    total_tax: str
    total_discounts: str
    total_line_items_price: str
    total_shipping_price: str = "0.00"
    currency: str
    presentment_currency: str | None
    taxes_included: bool
    confirmed: bool
    buyer_accepts_marketing: bool
    referring_site: str | None
    landing_site: str | None
    cancel_reason: str | None
    user_id: int | None
    customer_id: int | None
    app_id: int | None
    utm_parameters: dict | None


class ShopifyOrderCreate(ShopifyOrderBase):
    pass


class ShopifyOrderUpdate(ShopifyOrderBase):
    pass
