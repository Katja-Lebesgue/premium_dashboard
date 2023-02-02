import datetime
from pydantic import BaseModel


class CreativeTabInformationBase(BaseModel):
    id: int | None
    shop_id: int
    reference_date: datetime.date
    ads_generated: int
    tries_remaining: int
    purchased_credits_remaining: int
    counter: int
    terms_of_service_read: bool


class CreativeTabInformationCreate(CreativeTabInformationBase):
    id: int | None = None
    ads_generated: int = 0
    tries_remaining: int = 30
    purchased_credits_remaining: int = 0
    counter: int = 0
    terms_of_service_read: bool = False


class CreativeTabInformationUpdate(BaseModel):
    reference_date: datetime.date | None
    ads_generated: int | None
    tries_remaining: int | None
    purchased_credits_remaining: int | None
    counter: int | None
    terms_of_service_read: bool | None
