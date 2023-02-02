import datetime

from pydantic import BaseModel


class GoogleAdsInsightsBase(BaseModel):
    clicks: int
    impressions: int
    cost_micros: int
    conversions: float
    total_conversion_value: float
    conversions_purchase: float
    total_purchase_value: float
    spend: float


class GoogleAdsInsightsCreate(GoogleAdsInsightsBase):
    shop_id: int
    google_account_id: int
    date: datetime.date


class GoogleAdsInsightsUpdate(GoogleAdsInsightsBase):
    pass
