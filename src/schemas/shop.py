from datetime import date, datetime

from pydantic import EmailStr, Field
from src.models.enums import EcommercePlatform
from src.schemas.api_model import APIModel
from src.schemas.base import OrmBase


class ShopBase(APIModel):
    name: str | None = None
    onboarded: bool | None = False
    billing_date: date | None = None
    rapp_shop: bool | None = False
    currency: str | None = None
    iana_timezone: str | None = None
    location: str | None = None
    contact_email: EmailStr | None = None
    onboarding_completed: bool | None = False
    shopify_billing_plan: str | None = None
    partner_development: bool | None = False
    install_date: datetime | None = None
    installed: bool | None = True
    contact_name: str | None = None
    shop_name: str | None = None
    mailchimp_subscriber_hash: str | None = None
    owner_id: str | None = None
    platform: EcommercePlatform | None = None
    weekly_report: bool | None = None


class ShopCreate(ShopBase):
    name: str
    platform: EcommercePlatform
    installed: bool = True
    install_date: datetime = Field(default_factory=datetime.now)
    weekly_report: bool = True


class ShopUpdate(ShopBase):
    pass


class ShopUpdateAPI(APIModel):
    contact_email: EmailStr | None = None
    contact_name: str | None = None
    onboarding_completed: bool | None = False
    weekly_report: bool | None = True


class Shop(ShopBase):
    id: int

    class Config:
        orm_mode = True


class InternalShop(OrmBase):
    name: str | None
