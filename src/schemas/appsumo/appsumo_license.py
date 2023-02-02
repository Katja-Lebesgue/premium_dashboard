from pydantic import BaseModel
from src.models.enums.appsumo import Plan


class AppsumoLicenseBase(BaseModel):
    plan: Plan


class AppsumoLicenseCreate(AppsumoLicenseBase):
    product_key: str
    user_id: str


class AppsumoLicenseUpdate(AppsumoLicenseBase):
    pass


class AppSumoLicense(AppsumoLicenseBase):
    class Config:
        orm_mode = True
