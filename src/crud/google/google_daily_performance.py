from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from src.crud.base import CRUDBase
from src.crud.utils import get_performance
from src.models import *
from src.models import GoogleDailyPerformance
from src.schemas.google import (GoogleDailyPerformanceCreate,
                                GoogleDailyPerformanceUpdate)
from src.utils import *


class CRUDGoogleDailyPerformance(
    CRUDBase[GoogleDailyPerformance, GoogleDailyPerformanceCreate, GoogleDailyPerformanceUpdate]
):
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
            account_model=GoogleAdAccount,
            db=db,
            shop_id=shop_id,
            ad_id=ad_id,
            start_date=start_date,
            end_date=end_date,
            period=period,
            cast_to_date=cast_to_date,
            extra_column_names=["type"],
        )
        df = df.rename(columns={"adgroup_id_": "adset_id", "type": "campaign_type"})
        return df


ga_daily_performance = CRUDGoogleDailyPerformance(GoogleDailyPerformance)
