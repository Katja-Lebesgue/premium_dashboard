from pydantic import BaseModel
from src.models import enums
from src.schemas.api_model import APIModel


class CredentialsBase(BaseModel):
    id: int | None = None
    access_token: str | None = None
    credentials_provider: enums.CredentialsProvider | None = None
    refresh_token: str | None = None
    scope: str | None = None
    shop_id: int | None = None
    additional_data: dict | None = None


class CredentialsCreate(CredentialsBase):
    access_token: str
    credentials_provider: enums.CredentialsProvider
    scope: str
    shop_id: int


class CredentialsUpdate(CredentialsBase):
    access_token: str | None
    refresh_token: str | None
    additional_data: dict | None
    scope: str | None


class KlaviyoCredenialsInput(APIModel):
    private_key: str


class KlaviyoCredenialsResponse(APIModel):
    success: bool
    error: str | None = None
