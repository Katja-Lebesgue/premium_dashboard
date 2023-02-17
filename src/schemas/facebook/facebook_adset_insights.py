from datetime import date as date_type
from typing import Any

from pydantic import BaseModel, Field
from src.schemas.helpers import FieldAccessMetaclass


class FacebookAdsetInsightsBase(BaseModel):
    clicks: int | None = None
    link_clicks: int = 0
    impressions: int | None = None
    spend: float | None = None
    purchases: int = 0
    purchases_conversion_value: float = 0


class FacebookAdsetInsightsCreate(FacebookAdsetInsightsBase):
    shop_id: int
    account_id: str = Field(..., alias="account_id")
    adset_id: str
    date: date_type = Field(..., alias="date_start")


class FacebookAdsetInsightsUpdate(FacebookAdsetInsightsBase):
    pass


class FacebookAdsetInsightsField(FacebookAdsetInsightsBase, metaclass=FieldAccessMetaclass):
    pass
