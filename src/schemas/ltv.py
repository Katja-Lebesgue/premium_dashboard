import datetime

from pydantic import BaseModel

from src.schemas import LtvMetric


class LtvBarplotElement(BaseModel):
    order_period: str
    value_new: float | None
    value_repeat: float | None


class LtvBreakdownsBase(BaseModel):
    shop_id: int
    breakdown_type: str
    breakdown_value: str
    last_day_of_period: datetime.date
    period_length_in_months: int
    period_type: str


class LtvBreakdownsCreate(LtvBreakdownsBase):
    ltv: float | None
    churn_rate: float | None
    retention_rate: float | None


class LtvBreakdownsUpdate(LtvBreakdownsBase):
    ltv: float | None = None
    churn_rate: float | None = None
    retention_rate: float | None = None


class CohortElem(BaseModel):
    cohort: str
    value: float | None
    x: int
    y: int
    predicted: bool


class CohortAvgElem(BaseModel):
    diff: int
    value: float | None


class Cohorts(BaseModel):
    per_cohort: list[CohortElem]
    average: list[CohortAvgElem]


class LtvPlot(BaseModel):
    ltv: list[CohortAvgElem]
    cac: float | None


class LtvStats(BaseModel):
    data: list
    max_values: dict


class LtvMetricsInfo(BaseModel):
    metric_info: list[LtvMetric]
    metric_default_sort: list[str]
