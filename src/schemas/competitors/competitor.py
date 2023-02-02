from pydantic import BaseModel

from src.schemas.api_model import APIModel


class Competitor(APIModel):
    id: int
    competitor_logo: str | None
    competitor_name: str | None
    facebook_page_id: int | None
    facebook_page_url: str | None
    website: str | None
    app_user: bool

    class Config:
        orm_mode = True


class InternalCompetitor(Competitor):
    active: bool
    checked: bool
    shop_id: int | None


class CompetitorBase(BaseModel):
    pass


class CompetitorCreate(CompetitorBase):
    website: str
    competitor_name: str
    facebook_page_url: str | None


class CompetitorUpdate(BaseModel):
    pass


class CompetitorEdit(APIModel):
    competitor_name: str | None
    facebook_page_id: int | None
    facebook_page_url: str | None
    website: str | None
