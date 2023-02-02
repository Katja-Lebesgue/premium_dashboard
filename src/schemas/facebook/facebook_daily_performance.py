from datetime import date
from typing import Any

from pydantic import BaseModel
from src.schemas.helpers import FieldAccessMetaclass


class FacebookDailyPerformanceBase(BaseModel):
    adset_id: str
    campaign_id: str
    spend: float | None = None
    impressions: int | None = None
    clicks: int | None = None
    link_clicks: int = 0
    landing_page_views: int = 0
    add_to_cart: int = 0
    initiate_checkout: int = 0
    purchases: int = 0
    actions: list[Any] | None = None
    action_values: list[Any] | None = None
    purchases_conversion_value: float = 0


class FacebookDailyPerformanceCreate(FacebookDailyPerformanceBase):
    shop_id: int
    account_id: str
    ad_id: str
    date_start: date


class FacebookDailyPerformanceUpdate(FacebookDailyPerformanceBase):
    pass


class FacebookDailyPerformanceField(FacebookDailyPerformanceBase, metaclass=FieldAccessMetaclass):
    pass
