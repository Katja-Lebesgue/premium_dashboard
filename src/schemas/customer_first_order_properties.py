from datetime import datetime
from pydantic import BaseModel


class CustomerFirstOrderPropertiesBase(BaseModel):
    shop_id: int
    customer_id: int
    order_id: int
    order_processed_at: datetime
    order_product_ids: list[int]
    order_utms: dict
    order_channel: str
    order_discount_codes: list[str]
    order_discount_titles: list[str]
    customer_default_country_name: str
    customer_default_province_name: str


class CustomerFirstOrderPropertiesCreate(CustomerFirstOrderPropertiesBase):
    shop_id: int
    customer_id: int
    order_id: int
    order_processed_at: datetime | None = None
    order_product_ids: list[int] = []
    order_utms: dict | None = None
    order_channel: str | None = None
    order_discount_codes: list[str] = []
    order_discount_titles: list[str] = []
    customer_default_country_name: str | None = None
    customer_default_province_name: str | None = None


class CustomerFirstOrderPropertiesUpdate(CustomerFirstOrderPropertiesBase):
    order_id: int
    order_processed_at: datetime | None = None
    order_product_ids: list[int] = []
    order_utms: dict | None = None
    order_channel: str | None = None
    order_discount_codes: list[str] = []
    order_discount_titles: list[str] = []
    customer_default_country_name: str | None = None
    customer_default_province_name: str | None = None
