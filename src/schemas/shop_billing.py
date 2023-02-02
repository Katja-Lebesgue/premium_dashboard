from datetime import datetime

from pydantic import BaseModel


class ShopBillingBase(BaseModel):
    id: int | None
    shop_id: int | None
    billing_plan: str | None
    amount: str | None
    active: bool = False


class ShopBillingCreate(ShopBillingBase):
    id: int | None = None
    shop_id: int
    billing_plan: str
    amount: str
    active: bool = False


class ShopBillingUpdate(BaseModel):
    active: bool
    updated_at: datetime | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None


class ShopBilling(ShopBillingBase):
    pass


class ShopBillingPlanAPI(BaseModel):
    price: float
    description: str
    billing_plan: str
    billing_interval: str
    type: str


class ShopEligibleBillingPlansAPI(BaseModel):
    advanced: ShopBillingPlanAPI
    advanced_annual: ShopBillingPlanAPI
    ultimate: ShopBillingPlanAPI
    ultimate_annual: ShopBillingPlanAPI
    advanced_minor: ShopBillingPlanAPI
    advanced_minor_annual: ShopBillingPlanAPI
    small_shop: bool
