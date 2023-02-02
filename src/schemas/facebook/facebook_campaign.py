import datetime

from pydantic import BaseModel, Field


class FacebookCampaignBase(BaseModel):
    name: str
    objective: str
    status: str
    created_time: datetime.datetime


class FacebookCampaignCreate(FacebookCampaignBase):
    shop_id: int
    account_id: str
    campaign_id: str = Field(..., alias="id")


class FacebookCampaignUpdate(FacebookCampaignBase):
    pass
