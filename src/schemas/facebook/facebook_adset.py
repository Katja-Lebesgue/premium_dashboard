from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field
from src.schemas.helpers import FieldAccessMetaclass


class FacebookAdsetBase(BaseModel):
    name: str
    optimization_goal: str
    targeting: dict[str, Any]
    status: str
    campaign_id: str
    created_time: datetime


class FacebookAdsetCreate(FacebookAdsetBase):
    shop_id: int
    account_id: str
    adset_id: str = Field(..., alias="id")


class FacebookAdsetUpdate(FacebookAdsetBase):
    pass


class FacebookAdsetField(FacebookAdsetBase, metaclass=FieldAccessMetaclass):
    pass
