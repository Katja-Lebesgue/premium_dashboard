from datetime import datetime
from pydantic import BaseModel


class ShopifyInventoryItemBase(BaseModel):
    id: int | None
    shop_id: int
    gid: str | None
    cost: str | None
    sku: str | None
    tracked: bool
    created_at: datetime | None
    updated_at: datetime | None


class ShopifyInventoryItemCreate(ShopifyInventoryItemBase):
    pass


class ShopifyInventoryItemUpdate(ShopifyInventoryItemBase):
    pass
