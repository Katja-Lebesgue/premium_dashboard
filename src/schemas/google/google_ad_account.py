from pydantic import Field

from src.schemas.api_model import APIModel


class GoogleAdAccountBase(APIModel):
    shop_id: int
    user_id: int
    google_id: int = Field(..., alias="account_id")
    name: str
    currency: str
    time_zone: str
    user_connected: bool 
    internally_connected: bool 


class GoogleAdAccountCreate(GoogleAdAccountBase):
    user_connected: bool = True
    internally_connected: bool = False
    login_customer_id: int | None = None


class GoogleAdAccountUpdate(GoogleAdAccountBase):
    pass


class GoogleAdAccountInLib(APIModel):
    account_id: int = Field(..., alias="id")
    name: str = Field(..., alias="descriptive_name")
    currency: str = Field(..., alias="currency_code")
    time_zone: str
    manager: bool

    class Config:
        orm_mode = True


class GoogleAdAccountResponse(APIModel):
    account_id: int
    account: GoogleAdAccountInLib | None = None
    login_customer_id: int | None = None
    error_message: str | None = None


class GoogleAdAccount(GoogleAdAccountBase):
    id: int

    class Config:
        orm_mode = True
