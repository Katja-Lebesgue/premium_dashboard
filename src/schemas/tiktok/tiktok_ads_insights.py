from datetime import date as date_type

from pydantic import BaseModel, Field
from src.schemas.helpers import FieldAccessMetaclass


class TikTokAdsInsightsBase(BaseModel):
    currency: str
    spend: float | None
    clicks: int | float | None
    impressions: int | float | None
    complete_payment: int | float | None
    total_complete_payment_rate: float | None
    add_to_cart: int | float | None
    initiate_checkout: int | float | None


class TikTokAdsInsightsCreate(TikTokAdsInsightsBase):
    shop_id: int
    tiktok_account_id: str = Field(..., alias="account_id")
    date: date_type = Field(..., alias="date_start")


class TikTokAdsInsightsUpdate(TikTokAdsInsightsBase):
    pass


class FacebookAdsInsightsField(TikTokAdsInsightsBase, metaclass=FieldAccessMetaclass):
    pass
