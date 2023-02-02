from datetime import date
from enum import Enum

from pydantic import BaseModel

from src.schemas.competitors.facebook_ad_from_library import FacebookAdFromLibrary
from src.models.enums.competitor.social_platform import SocialPlatform
from src.schemas.competitors.competitor_keywords import CompetitorKeywords
from src.schemas.api_model import APIModel


class ScanInfo(BaseModel):
    last_scan_date: date | None
    first_scan_date: date | None
    scan_message: str


class AdGroup(str, Enum):
    active_ads = "active_ads"
    inactive_ads = "inactive_ads"
    new_ads = "new_ads"
    turned_off_ads = "turned_off_ads"


class AdGroupSubtitle(str, Enum):
    active_ads = "Since last scan"
    inactive_ads = "Last 6 months"
    new_ads = "Since last scan"
    turned_off_ads = "Since last scan"


class AdsSummary(BaseModel):
    image: int
    video: int
    carousel: int
    dynamic_product: int
    dynamic_creative: int
    other: int
    screenshots: list[str]
    change: int | None


class AdPublishingDetail(BaseModel):
    ad_group: AdGroup
    subtitle: AdGroupSubtitle
    summary: AdsSummary


class CompetitorFacebookAd(BaseModel):
    ad: FacebookAdFromLibrary
    ad_groups: list[AdGroup]


class AdTextFeature(BaseModel):
    test: str
    title: str


class PublishedAdsByDate(BaseModel):
    date: date
    published_ads: int


class CompetitorAnalysisGallery(BaseModel):
    gallery: list[CompetitorFacebookAd]
    ad_text_features: list[AdTextFeature]


class HistoricalOverviewParameterName(str, Enum):
    frequency = "frequency"
    creativity = "creativity"
    stability = "stability"


class HistoricalOverviewParameterData(BaseModel):
    value: float
    score: float


class HistoricalOverviewParameter(BaseModel):
    name: HistoricalOverviewParameterName
    data: HistoricalOverviewParameterData


class WordcloudKeyword(BaseModel):
    keyword: CompetitorKeywords
    growth_class: str
    weight: float


class LandscapeMainMetricName(str, Enum):
    current_size = "current_size"
    mom_growth = "mom_growth"
    yoy_growth = "yoy_growth"


class LandscapeMainMetric(BaseModel):
    name: LandscapeMainMetricName
    value: float | None


class CompetitorsOverviewPeriod(str, Enum):
    monthly = "monthly"
    quarterly = "quarterly"
    biyearly = "biyearly"


class BrandKeywordVolume(BaseModel):
    period: date
    search_volume: int


class SocialMedia(BaseModel):
    platform: SocialPlatform
    followers_number: int


class CompetitorInfo(APIModel):
    id: int
    competitor_logo: str | None
    competitor_name: str | None
    facebook_page_id: int | None
    facebook_page_url: str | None
    website: str | None
    app_user: bool
    import_done: bool
