from datetime import date
from pydantic import BaseModel


class BusinessDailyBase(BaseModel):
    shop_id: int
    date: date
    orders: int | None = None
    revenue: float | None = None
    first_time_orders: int | None = None
    repeat_orders: int | None = None
    first_time_revenue: float | None = None
    repeat_revenue: float | None = None
    total_line_items_price: float | None = None
    total_tax: float | None = None
    total_discounts: float | None = None
    total_shipping_price: float | None = None
    aov: float | None = None
    first_time_aov: float | None = None
    repeat_aov: float | None = None
    cancelled_orders: int | None = None
    cancelled_revenue: float | None = None
    margin: float | None = None
    cogs: float | None = None


class BusinessDailyCreate(BusinessDailyBase):
    pass


class BusinessDailyUpdate(BusinessDailyBase):
    pass
