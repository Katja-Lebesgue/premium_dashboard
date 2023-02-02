from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field
from src.schemas.helpers import FieldAccessMetaclass


class TikTokAdBase(BaseModel):
    adset_id: str
    campaign_id: str
    creative_id: str | None
    name: str
    status: str
    created_time: datetime
    body_text: str | None
    creative: dict[str, Any]


class TikTokAdCreate(TikTokAdBase):
    shop_id: int
    account_id: str
    ad_id: str = Field(..., alias="id")


class TikTokAdUpdate(TikTokAdBase):
    pass


class TikTokAdField(TikTokAdBase, metaclass=FieldAccessMetaclass):
    pass
