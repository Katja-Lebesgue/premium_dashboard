import datetime

from pydantic import BaseModel


class RedFlagResultBase(BaseModel):
    pass


class RedFlagResultCreate(RedFlagResultBase):
    shop_id: int
    date: datetime.date
    test: str
    source: str
    result: str
    comment: str


class RedFlagResultUpdate(RedFlagResultBase):
    result: str
    comment: str
