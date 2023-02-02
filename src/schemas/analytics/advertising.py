from datetime import date
from typing import Any
from pydantic import BaseModel, Field

from src.enums.analytics.metric_format import MetricFormat


class AdvertisingMetrics(BaseModel):
    metrics_info: list[dict[str, bool | str]] = Field(..., alias="metricsInfo")
    table_sort: list[str] = Field(..., alias="tableSort")


class AdvertisingMetricsInfo(BaseModel):
    key: str
    name: str
    format: MetricFormat = MetricFormat.decimal
    default: bool = False
    default_fb: bool = False
    default_ga: bool = False


class AdvertisingTableDetails(BaseModel):
    id: str
    name: str
    status: str | None
    campaign_type: str | None
    campaign_id: str | None
    adset_id: str | None
    ad_id: str | None
    data: list[dict[str, float | str | date | None]]


class AdTreeNode(BaseModel):
    name: str
    campaign_type: str | None
    campaign_id: str | None
    adset_id: str | None
    ad_id: str | None


class AdvertisingTable(BaseModel):
    campaign_type: list[AdvertisingTableDetails] | None
    campaign: list[AdvertisingTableDetails] | None
    adset: list[AdvertisingTableDetails] | None
    ad: list[AdvertisingTableDetails] | None

    all_data: list[dict[str, float | Any]] | None
