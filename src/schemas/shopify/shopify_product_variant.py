from datetime import datetime
from pydantic import BaseModel


class ShopifyProductVariantBase(BaseModel):
    id: int
    shop_id: int
    product_id: int | None
    gid: str
    title: str
    sku: str | None
    price: str
    created_at: datetime | None
    updated_at: datetime | None
    taxable: bool
    requires_shipping: bool
    inventory_item_id: int | None


class ShopifyProductVariantCreate(ShopifyProductVariantBase):
    pass


class ShopifyProductVariantUpdate(ShopifyProductVariantBase):
    pass
