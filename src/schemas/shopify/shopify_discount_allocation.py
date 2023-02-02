from pydantic import BaseModel


class ShopifyDiscountAllocationBase(BaseModel):
    shop_id: int
    amount: str
    discount_application_index: int
    line_item_id: int


class ShopifyDiscountAllocationCreate(ShopifyDiscountAllocationBase):
    pass


class ShopifyDiscountAllocationUpdate(ShopifyDiscountAllocationBase):
    pass
