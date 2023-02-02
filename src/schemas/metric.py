from pydantic import BaseModel
from src.enums.analytics.metric_format import MetricFormat
from src.enums.comparison_sign import Sign


class MetricChange(BaseModel):
    metric_name: str
    metric_label: str
    metric_description: str
    value: float | None = None
    value_previous: float | None = None
    change: float | None = None
    sign: str | None = Sign.neutral.name


class CompareMetric(BaseModel):
    hover_info: str
    sign: str | None
    value: float | None
    value_compare: float | None
    comparison: float | None


class MetricAverage(BaseModel):
    metric_name: str
    metric_label: str
    metric_description: str
    value: float | None = None
    calculation_period: str | None = None


class BusinessMetric(BaseModel):
    name: str
    short_label: str | None = None
    label: str | None = None
    format: MetricFormat = MetricFormat.decimal


class LtvMetric(BaseModel):
    key: str
    format: MetricFormat
    name: str | None = None
    description: str | None = None
    default: bool = False
