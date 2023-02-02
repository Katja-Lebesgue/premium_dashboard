from datetime import datetime

from pydantic import BaseModel


class ShopifyCustomerBase(BaseModel):
    id: int
    shop_id: int
    gid: str
    email: str | None
    created_at: datetime | None
    updated_at: datetime | None
    account_state: str
    orders_count: int
    last_order_id: int | None
    first_order_id: int | None
    first_order_created_at: datetime | None
    tags: str | None
    total_spent: str
    tax_exempt: bool
    currency: str
    accepts_marketing: bool
    default_country: str | None
    default_province: str | None
    default_country_code: str | None
    default_province_code: str | None


class ShopifyCustomerCreate(ShopifyCustomerBase):
    pass


class ShopifyCustomerUpdate(ShopifyCustomerBase):
    pass
