import datetime
from pydantic import BaseModel, Field

from src.schemas import APIModel
from src.enums.copywriter.creativity_level import CreativityLevel


class CreativeTabAdsBase(BaseModel):
    id: int | None
    shop_id: int
    period: datetime.date
    ad_text: str
    ad_type: CreativityLevel
    specification: dict
    ad_viewed: bool
    reaction: int
    created_at: datetime.datetime


class CreativeTabAdsCreate(CreativeTabAdsBase):
    id: int | None = None
    shop_id: int
    period: datetime.date = Field(default_factory=datetime.date.today)
    ad_text: str
    ad_type: CreativityLevel
    specification: dict
    ad_viewed: bool = False
    reaction: int = 0
    created_at: datetime.datetime | None = Field(default_factory=datetime.datetime.now)


class CopywriterAd(APIModel):
    text: str
    id: int


class CopywriterInputBody(APIModel):
    url: str
    title: str
    description: str
    creativity: str


class CopywriterEmailInputBody(APIModel):
    ads: list[str]
    creativity: str | None = None


class CopywriterUpdateDescriptionInput(APIModel):
    new_description: str


class CopywriterUpdateDescriptionOutput(APIModel):
    old_description: str
    new_description: str


class CreativeTabAdsUpdate(CreativeTabAdsBase):
    pass


class CreativeTabAdsAPI(APIModel):
    id: int | None
    ad_text: str
    reaction: int
    created_at: datetime.datetime
