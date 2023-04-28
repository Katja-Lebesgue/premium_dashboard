from datetime import datetime

from pydantic import BaseModel


class ImageBase(BaseModel):
    source_id: str | None
    source: str | None
    shop_id: int | None
    width: int | None
    height: int | None
    created_at: datetime | None
    url: str | None
    image_hash: str | None
    additional_data: dict | None
    internally_saved: bool | None
    last_refreshed: datetime | None


class ImageCreate(ImageBase):
    pass


class ImageUpdate(ImageBase):
    pass
