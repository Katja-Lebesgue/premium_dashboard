from datetime import date, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.expression import literal

from src.crud.base import CRUDBase
from src.models.facebook import FacebookAdset, FacebookAdAccount, FacebookDailyPerformance
from src.schemas.facebook.facebook_daily_performance import (
    FacebookDailyPerformanceCreate,
    FacebookDailyPerformanceUpdate,
)

from src.utils.common import element_to_list


class CRUDFacebookDailyPerformance(
    CRUDBase[FacebookDailyPerformance, FacebookDailyPerformanceCreate, FacebookDailyPerformanceUpdate]
):
    def get(
        self, db: Session, shop_id: int, account_id: str, ad_id: str, date_start: date
    ) -> FacebookDailyPerformance | None:
        return db.query(self.model).get((shop_id, account_id, ad_id, date_start))

    def query_performance(
        self,
        db: Session,
        shop_id: str | list[str] = None,
        ad_id: str | list[str] = None,
        start_date: str = None,
        end_date: str = date.today().strftime("%Y-%m-%d"),
        add_currency: bool = True,
        monthly: bool = True,
    ) -> Query:

        group_columns = [
            FacebookDailyPerformance.ad_id,
            FacebookDailyPerformance.shop_id,
            FacebookDailyPerformance.account_id,
        ]

        performance_columns = [
            func.sum(FacebookDailyPerformance.impressions).label("impr"),
            func.sum(FacebookDailyPerformance.link_clicks).label("link_clicks"),
            func.sum(FacebookDailyPerformance.purchases).label("purch"),
            func.sum(FacebookDailyPerformance.spend).label("spend"),
            func.sum(FacebookDailyPerformance.purchases_conversion_value).label("purch_value"),
        ]

        columns = group_columns + performance_columns

        if monthly:
            year_month_col = func.concat(
                func.extract("year", FacebookDailyPerformance.date_start),
                "-",
                func.to_char(func.extract("month", FacebookDailyPerformance.date_start), "fm00"),
            )
            columns.append(year_month_col.label("year_month"))
            group_columns.append(year_month_col)

        if add_currency:
            columns.append(FacebookAdAccount.currency)
            group_columns.append(FacebookAdAccount.currency)

        query = db.query(*columns)

        if ad_id is not None:
            ad_id = element_to_list(ad_id)
            query = query.filter(FacebookDailyPerformance.ad_id.in_(ad_id))

        if shop_id is not None:
            shop_id = element_to_list(shop_id)
            query = query.filter(FacebookDailyPerformance.shop_id.in_(shop_id))

        if start_date is not None:
            query = query.filter(
                FacebookDailyPerformance.date_start >= start_date,
                FacebookDailyPerformance.date_start <= end_date,
            )

        query = query.group_by(*group_columns)

        if add_currency:
            query = query.join(
                FacebookAdAccount,
                FacebookDailyPerformance.account_id == FacebookAdAccount.facebook_id,
            )

        query = query.distinct()

        return query


crud_fb_daily_performance = CRUDFacebookDailyPerformance(FacebookDailyPerformance)
