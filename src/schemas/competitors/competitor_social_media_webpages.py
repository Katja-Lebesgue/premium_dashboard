from pydantic import BaseModel


class CompetitorSocialMediaWebpageseBase(BaseModel):
    pass


class CompetitorSocialMediaWebpagesCreate(CompetitorSocialMediaWebpageseBase):
    platform: str
    url: str
    competitor_id: int


class CompetitorSocialMediaWebpagesUpdate(CompetitorSocialMediaWebpageseBase):
    pass
