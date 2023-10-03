from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from src.crud.base import CRUDBase
from src.crud.utils import get_performance
from src.models import *
from src.schemas.facebook.facebook_daily_performance import *
from src.utils import *


class CRUDFacebookDailyPerformance(
    CRUDBase[FacebookDailyPerformance, FacebookDailyPerformanceCreate, FacebookDailyPerformanceUpdate]
):
    def get(
        self, db: Session, shop_id: int, account_id: str, ad_id: str, date_start: date
    ) -> FacebookDailyPerformance | None:
        return db.query(self.model).get((shop_id, account_id, ad_id, date_start))

    def get_performance(
        self,
        db: Session,
        shop_id: str | list[str] = None,
        ad_id: str | list[str] = None,
        start_date: date | str | None = None,
        end_date: date | str = date.today(),
        period: Period = Period.year_month,
        cast_to_date: bool = False,
    ) -> pd.DataFrame:
        df = get_performance(
            performance_model=self.model,
            account_model=FacebookAdAccount,
            db=db,
            shop_id=shop_id,
            ad_id=ad_id,
            start_date=start_date,
            end_date=end_date,
            period=period,
            cast_to_date=cast_to_date,
        )
        df = df.rename(columns={"adgroup_id_": "adset_id"})
        return df


fb_daily_performance = CRUDFacebookDailyPerformance(FacebookDailyPerformance)
