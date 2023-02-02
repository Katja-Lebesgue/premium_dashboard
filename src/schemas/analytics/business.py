from typing import Any
from pydantic import BaseModel, Field


class BusinessMetricsInfo(BaseModel):
    metrics_info: Any = Field(..., alias="metricsInfo")
    table_sort: Any = Field(..., alias="tableSort")
    sort_info: Any = Field(..., alias="sortInfo")


class BusinessTableAPI(BaseModel):
    data: list[dict]
    total: dict


class BusinessGraphAPI(BaseModel):
    data: list[dict]


class PredictRevenueAPI(BaseModel):
    pacing_revenue: float
    month_name: str
