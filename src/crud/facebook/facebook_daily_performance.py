from datetime import date, timedelta

from loguru import logger
from sqlalchemy import and_, case, func
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query
import pandas as pd


from src.crud.utils import get_performance
from src.crud.base import CRUDBase
from src.crud.currency_exchange_rate import currency_exchange_rate as crud_currency_exchange_rate
from src.models import *
from src.schemas.facebook.facebook_daily_performance import *
from src.utils import element_to_list


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
        start_date: str = None,
        end_date: str = date.today().strftime("%Y-%m-%d"),
        monthly: bool = True,
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
            monthly=monthly,
            cast_to_date=cast_to_date,
        )
        df = df.rename(columns={"adgroup_id_": "adset_id"})
        return df


fb_daily_performance = CRUDFacebookDailyPerformance(FacebookDailyPerformance)
