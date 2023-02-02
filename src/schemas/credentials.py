from typing import Optional

from pydantic import BaseModel
from src.models import enums


class CredentialsBase(BaseModel):
    pass


class CredentialsCreate(CredentialsBase):
    access_token: str
    credentials_provider: enums.CredentialsProvider
    refresh_token: Optional[str] = None
    scope: str
    shop_id: int


class CredentialsUpdate(CredentialsBase):
    access_token: str
