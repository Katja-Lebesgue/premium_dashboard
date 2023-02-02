from datetime import date

from pydantic import BaseModel


class CurrencyExchangeRateBase(BaseModel):
    rate_from_usd: float
    date: date
    code: str


class CurrencyExchangeRateCreate(CurrencyExchangeRateBase):
    pass


class CurrencyExchangeRateUpdate(CurrencyExchangeRateBase):
    pass


class CurrencyExchangeRateInDBBase(CurrencyExchangeRateBase):
    id: int

    class Config:
        orm_mode = True


class CurrencyExchangeRate(CurrencyExchangeRateInDBBase):
    pass
