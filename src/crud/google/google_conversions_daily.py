from datetime import date

from sqlalchemy.orm import Session
from src.crud.base import CRUDBase
from src.models.google.google_conversions_daily import GoogleConversionsDaily
from src.schemas.google.google_conversions_daily import (
    GoogleConversionsDailyCreate,
    GoogleConversionsDailyUpdate,
)


class CRUDGoogleConversionsDaily(
    CRUDBase[GoogleConversionsDaily, GoogleConversionsDailyCreate, GoogleConversionsDailyUpdate]
):
    def get(
        self, db: Session, shop_id: int, google_account_id: int, conversion_id: int, date: date
    ) -> GoogleConversionsDaily | None:
        return db.query(self.model).get((shop_id, google_account_id, conversion_id, date))


ga_conversions_daily = CRUDGoogleConversionsDaily(GoogleConversionsDaily)
