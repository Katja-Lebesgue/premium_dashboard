from pydantic import Field
from datetime import date
from src.schemas.api_model import APIModel


class TikTokAdAccountBase(APIModel):
    tiktok_id: str = Field(..., alias="account_id")
    name: str
    currency: str
    shop_id: int
    created_time: date
    time_zone: str
    timezone_offset_hours_utc: int
    connected: bool


class TikTokAdAccountCreate(TikTokAdAccountBase):
    connected: bool = True


class TikTokAdAccountUpdate(TikTokAdAccountBase):
    pass


class TikTokAdAccountAPI(APIModel):
    advertiser_id: str = Field(..., alias="account_id")
    name: str
    currency: str
    create_time: date = Field(..., alias="created_time")
    display_timezone: str = Field(..., alias="time_zone")


class TikTokAdAccount(TikTokAdAccountBase):
    id: int

    class Config:
        orm_mode = True
