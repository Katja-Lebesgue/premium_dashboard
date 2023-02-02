from pydantic import BaseModel, Field


class FacebookCustomaudienceBase(BaseModel):
    subtype: str


class FacebookCustomaudienceCreate(FacebookCustomaudienceBase):
    shop_id: int
    account_id: str
    customaudience_id: str = Field(..., alias="id")


class FacebookCustomaudienceUpdate(FacebookCustomaudienceBase):
    pass
