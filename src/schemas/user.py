from typing import Optional

from pydantic import BaseModel, EmailStr
from src import schemas
from src.schemas.api_model import APIModel


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[str] = None

    class Config:
        orm_mode = True


class ResetPasswordBody(APIModel):
    new_password: str
    token: str


class User(UserInDBBase):
    max_shop_number: int
    shops: list[schemas.Shop]
    purchase: schemas.AppsumoPurchase | None
