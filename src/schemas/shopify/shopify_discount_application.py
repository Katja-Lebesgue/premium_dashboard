from pydantic import BaseModel


class ShopifyDiscountApplicationBase(BaseModel):
    shop_id: int
    order_id: int | None
    index: int
    type: str
    title: str | None
    description: str | None
    code: str | None
    value: str
    value_type: str | None
    allocation_method: str | None
    target_selection: str | None
    target_type: str | None


class ShopifyDiscountApplicationCreate(ShopifyDiscountApplicationBase):
    pass


class ShopifyDiscountApplicationUpdate(ShopifyDiscountApplicationBase):
    pass
