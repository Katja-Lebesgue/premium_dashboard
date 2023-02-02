from pydantic import BaseModel


class ShopifyLineItemBase(BaseModel):
    id: int
    shop_id: int
    order_id: int | None
    gid: str
    title: str
    variant_id: int | None
    variant_title: str | None
    quantity: int
    sku: str | None
    product_id: int | None
    name: str
    price: str
    total_discount: str
    total_tax: str = "0.00"


class ShopifyLineItemCreate(ShopifyLineItemBase):
    pass


class ShopifyLineItemUpdate(ShopifyLineItemBase):
    pass
