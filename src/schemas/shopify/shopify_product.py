from datetime import datetime
from pydantic import BaseModel

from src.schemas.api_model import APIModel


class ShopifyProductBase(BaseModel):
    id: int
    shop_id: int
    gid: str
    title: str
    description: str | None = None
    extracted_description: str | None = None
    status: str | None = None
    vendor: str | None
    handle: str
    product_type: str
    tags: str
    created_at: datetime | None
    updated_at: datetime | None
    published_at: datetime | None


class ShopifyProductCreate(ShopifyProductBase):
    pass


class ShopifyProductUpdate(ShopifyProductBase):
    pass


class ShopifyProductAPI(APIModel):
    id: int
    shop_id: int
    url: str
    title: str
    description: str
    active: bool
