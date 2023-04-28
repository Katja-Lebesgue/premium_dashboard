from typing import Any

from src.schemas.api_model import APIModel


class AdCreativeFeaturesBase(APIModel):
    creative_id: str
    feature: str
    value: dict[str, Any]


class AdCreativeFeaturesCreate(AdCreativeFeaturesBase):
    shop_id: int
    account_id: str
    ad_id: str


class AdCreativeFeaturesUpdate(AdCreativeFeaturesBase):
    pass
