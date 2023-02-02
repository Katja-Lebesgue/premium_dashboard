from datetime import date, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.expression import literal

from src.crud.base import CRUDBase
from src.models.facebook.facebook_daily_performance import FacebookDailyPerformance
from src.models.facebook.facebook_adset import FacebookAdset
from src.schemas.facebook.facebook_daily_performance import (
    FacebookDailyPerformanceCreate,
    FacebookDailyPerformanceUpdate,
)
from src.utils.common import timed_lru_cache
from src.utils.period import PeriodHandlerBase, PeriodTypeBase


class CRUDFacebookDailyPerformance(
    CRUDBase[FacebookDailyPerformance, FacebookDailyPerformanceCreate, FacebookDailyPerformanceUpdate]
):
    def get(
        self, db: Session, shop_id: int, account_id: str, ad_id: str, date_start: date
    ) -> FacebookDailyPerformance | None:
        return db.query(self.model).get((shop_id, account_id, ad_id, date_start))


fb_daily_performance = CRUDFacebookDailyPerformance(FacebookDailyPerformance)
