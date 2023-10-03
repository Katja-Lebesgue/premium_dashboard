from datetime import date, datetime

from pydantic import EmailStr, Field

from src.models.enums import EcommercePlatform
from src.schemas.api_model import APIModel
from src.schemas.base import OrmBase


class ShopBase(APIModel):
    name: str | None = None
    billing_date: date | None = None
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
    owner_id: int | None = None
    platform: EcommercePlatform | None = None
    email_settings: dict | None = None
    intro_modal_shown: bool | None = None
    modules: str | None = None
    app: str | None = None
    app_store_install: bool | None = None


class ShopCreate(ShopBase):
    pass


class ShopUpdate(ShopBase):
    pass


class Shop(ShopBase):
    id: int
    limited_access: bool

    class Config:
        orm_mode = True
