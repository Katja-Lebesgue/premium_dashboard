from datetime import date, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.expression import literal
from loguru import logger

from src.crud.base import CRUDBase
from src.models import *
from src.schemas.facebook.facebook_daily_performance import *
from src.crud.currency_exchange_rate import crud_currency_exchange_rate

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
            self.model.ad_id,
            self.model.shop_id,
            self.model.account_id,
        ]

        performance_columns = [
            func.sum(self.model.impressions).label("impr"),
            func.sum(self.model.link_clicks).label("link_clicks"),
            func.sum(self.model.purchases).label("purch"),
            func.sum(self.model.spend).label("spend"),
            func.sum(self.model.purchases_conversion_value).label("purch_value"),
        ]

        columns = group_columns + performance_columns

        if monthly:
            year_month_col = func.concat(
                func.extract("year", self.model.date_start),
                "-",
                func.to_char(func.extract("month", self.model.date_start), "fm00"),
            )
            columns.append(year_month_col.label("year_month"))
            group_columns.append(year_month_col)

        if add_currency:
            columns.append(FacebookAdAccount.currency)
            group_columns.append(FacebookAdAccount.currency)

        query = db.query(*columns)

        if ad_id is not None:
            ad_id = element_to_list(ad_id)
            query = query.filter(self.model.ad_id.in_(ad_id))

        if shop_id is not None:
            shop_id = element_to_list(shop_id)
            query = query.filter(self.model.shop_id.in_(shop_id))

        if start_date is not None:
            query = query.filter(
                self.model.date_start >= start_date,
                self.model.date_start <= end_date,
            )

        query = query.group_by(*group_columns)

        if add_currency:
            query = query.join(
                FacebookAdAccount,
                (self.model.account_id == FacebookAdAccount.facebook_id)
                & (self.model.shop_id == FacebookAdAccount.shop_id),
            )

        query = query.distinct()

        return query

    def query_budget_split_by_target(
        self,
        db: Session,
        shop_id: int | list[int] = None,
        start_date: str = None,
        end_date: str = date.today().strftime("%Y-%m-%d"),
    ) -> Query:
        currency_subquery = crud_currency_exchange_rate.query_current_rates(db=db).subquery()

        group_columns = [
            self.model.shop_id,
            FacebookAdset.target,
        ]

        performance_columns = [
            func.sum(self.model.spend / currency_subquery.c.rate_from_usd).label("spend"),
        ]

        columns = group_columns + performance_columns

        query = db.query(*columns)

        if shop_id is not None:
            shop_id = element_to_list(shop_id)
            query = query.filter(self.model.shop_id.in_(shop_id))

        if start_date is not None:
            query = query.filter(
                self.model.date_start >= start_date,
                self.model.date_start <= end_date,
            )

        # query = query.group_by(*group_columns)

        query = query.join(
            FacebookAdset,
            (self.model.shop_id == FacebookAdset.shop_id)
            & (self.model.account_id == FacebookAdset.account_id)
            & (self.model.adset_id == FacebookAdset.adset_id),
        )

        query = query.join(
            FacebookAdAccount,
            (self.model.account_id == FacebookAdAccount.facebook_id)
            & (self.model.shop_id == FacebookAdAccount.shop_id),
        )

        query = query.join(currency_subquery, FacebookAdAccount.currency == currency_subquery.c.code)

        query = query.group_by(*group_columns)

        return query


crud_fb_daily_performance = CRUDFacebookDailyPerformance(FacebookDailyPerformance)
