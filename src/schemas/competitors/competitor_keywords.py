import datetime
from typing import Optional

from pydantic import BaseModel


class CompetitorKeywordsBase(BaseModel):
    pass


class CompetitorKeywordsCreate(CompetitorKeywordsBase):
    competitor_id: int
    keyword_text: str
    avg_monthly_searches: int
    keyword_growth: float
    date: str
    competition: str


class CompetitorKeywordsUpdate(CompetitorKeywordsBase):
    pass


class CompetitorKeywordsInDBBase(CompetitorKeywordsBase):
    id: Optional[int] = None
    competitor_id: Optional[int] = None
    keyword_text: Optional[str] = None
    avg_monthly_searches: Optional[int] = None
    keyword_growth: Optional[float] = None
    date: Optional[datetime.date] = None

    class Config:
        orm_mode = True


class CompetitorKeywords(CompetitorKeywordsInDBBase):
    competition: Optional[str]
    competing_brands: Optional[list[str]]
