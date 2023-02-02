from datetime import date
from typing import Optional

from pydantic import BaseModel


class FacebookAdFromLibraryBase(BaseModel):
    pass


class FacebookAdFromLibraryDB(FacebookAdFromLibraryBase):
    id: int
    storage_date: date
    competitor_id: int
    ad_data: dict | None = None
    page_id: int
    ad_screenshot_url: str | None = None
    checked: bool


class FacebookAdFromLibraryCreate(FacebookAdFromLibraryDB):
    pass


class FacebookAdFromLibraryUpdate(FacebookAdFromLibraryDB):
    pass


class FacebookAdFromLibraryInDBBase(FacebookAdFromLibraryBase):
    id: Optional[int] = None
    storage_date: Optional[date] = None
    ad_screenshot_url: Optional[str] = None

    class Config:
        orm_mode = True


class FacebookAdFromLibrary(FacebookAdFromLibraryInDBBase):
    ad_type: Optional[str] = None
    ad_text: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    running_days: Optional[int] = None
    ad_text_features: Optional[list[dict]] = None
