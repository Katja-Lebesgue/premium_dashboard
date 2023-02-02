from datetime import datetime

from pydantic import BaseModel
from src.models.enums.appsumo.plan import Plan


class AppsumoPurchase(BaseModel):
    id: int
    invoice_item_uuid: str
    plan: Plan
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
