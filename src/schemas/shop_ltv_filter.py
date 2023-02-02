from src.schemas import APIModel


class ShopLtvFilterBase(APIModel):
    name: str
    params: dict
    default: bool


class ShopLtvFilterCreate(ShopLtvFilterBase):
    shop_id: int


class ShopLtvFilterUpdate(APIModel):
    name: str | None
    default: bool | None
    params: dict | None


class ShopLtvFilterIn(APIModel):
    name: str
    params: dict


class ShopLtvFilter(ShopLtvFilterBase):
    id: int

    class Config:
        orm_mode = True
