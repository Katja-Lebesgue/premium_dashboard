from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field
from src.schemas.helpers import FieldAccessMetaclass


class FacebookAdBase(BaseModel):
    adset_id: str
    campaign_id: str
    creative_id: str | None
    name: str
    status: str
    created_time: datetime
    body_text: str | None
    creative: dict[str, Any]
    ad_language: str | None


class FacebookAdCreate(FacebookAdBase):
    shop_id: int
    account_id: str
    ad_id: str = Field(..., alias="id")


class FacebookAdUpdate(FacebookAdBase):
    pass


class FacebookAdField(FacebookAdBase, metaclass=FieldAccessMetaclass):
    pass
