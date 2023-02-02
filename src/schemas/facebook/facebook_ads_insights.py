from datetime import date as date_type
from typing import Any

from pydantic import BaseModel, Field
from src.schemas.helpers import FieldAccessMetaclass


class FacebookAdsInsightsBase(BaseModel):
    clicks: int | None = None
    link_clicks: int = 0
    outbound_clicks: int = 0
    cpc: float | None = None
    cpm: float | None = None
    ctr: float | None = None
    impressions: int | None = None
    reach: int | None = None
    spend: float | None = None
    purchases: int = 0
    oned_view_purchases: int = 0
    oned_click_purchases: int = 0
    purchases_conversion_value: float = 0
    actions: list[Any]
    action_values: list[Any]


class FacebookAdsInsightsCreate(FacebookAdsInsightsBase):
    shop_id: int
    facebook_account_id: str = Field(..., alias="account_id")
    date: date_type = Field(..., alias="date_start")


class FacebookAdsInsightsUpdate(FacebookAdsInsightsBase):
    pass


class FacebookAdsInsightsField(FacebookAdsInsightsBase, metaclass=FieldAccessMetaclass):
    pass
