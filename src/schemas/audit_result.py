from datetime import date

from pydantic import BaseModel

from src.enums.common.ad_platform import AdPlatform
from src.enums.audit_result.check_type import CheckType
from src.enums.audit_result.status_type import StatusType


class AuditResult(BaseModel):
    date: date
    type: CheckType
    status: StatusType
    description: str
    ad_platform: AdPlatform
    title: str
    button_copy: str | None
    button_type: str | None
    button_url: str | None
    link_plan: str | None
    steps: list[str] | None
    cta: str | None
    average_rate: int | None
    new: bool
    score: int | None
