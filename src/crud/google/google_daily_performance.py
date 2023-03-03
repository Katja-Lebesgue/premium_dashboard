from datetime import date
import pandas as pd


from sqlalchemy.orm import Session, Query
from sqlalchemy import and_, func
from sqlalchemy.sql.expression import literal

from src.feature_extractors import add_performance_columns
from src.crud.base import CRUDBase
from src.models import GoogleDailyPerformance
from src.schemas.google import GoogleDailyPerformanceCreate, GoogleDailyPerformanceUpdate
from src.utils.common import element_to_list
from src.models import *
from src.crud.currency_exchange_rate import crud_currency_exchange_rate


class CRUDGoogleDailyPerformance(
    CRUDBase[GoogleDailyPerformance, GoogleDailyPerformanceCreate, GoogleDailyPerformanceUpdate]
):
    def query_performance(
        self,
        db: Session,
        shop_id: str | list[str] = None,
        ad_id: str | list[str] = None,
        start_date: str = None,
        end_date: str = date.today().strftime("%Y-%m-%d"),
        add_currency: bool = True,
        monthly: bool = True,
        add_type: bool = True,
    ) -> Query:
        group_columns = [
            self.model.ad_id,
            self.model.shop_id,
            self.model.account_id,
        ]

        performance_columns = [
            func.sum(self.model.impressions).label("impr"),
            func.sum(self.model.clicks).label("link_clicks"),
            func.sum(self.model.conversions_purchase).label("purch"),
            func.sum(self.model.spend).label("spend"),
            func.sum(self.model.conversions_value_purchase).label("purch_value"),
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
            columns.append(GoogleAdAccount.currency)
            group_columns.append(GoogleAdAccount.currency)

        if add_type:
            columns.append(GoogleAdgroup.type)
            group_columns.append(GoogleAdgroup.type)

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
                GoogleAdAccount,
                self.model.account_id == GoogleAdAccount.google_id,
            )

        if add_type:
            query = query.join(
                GoogleAdgroup,
                (self.model.account_id == GoogleAdgroup.account_id)
                & (self.model.adgroup_id == GoogleAdgroup.adgroup_id)
                & (self.model.shop_id == GoogleAdgroup.shop_id),
            )

        return query

    def ping_performance(
        self,
        db: Session,
        shop_id: str | list[str] = None,
        ad_id: str | list[str] = None,
        start_date: str = None,
        end_date: str = date.today().strftime("%Y-%m-%d"),
        add_currency: bool = True,
        monthly: bool = True,
        add_type: bool = True,
    ) -> pd.DataFrame:
        query = self.query_performance(
            db=db,
            shop_id=shop_id,
            ad_id=ad_id,
            start_date=start_date,
            end_date=end_date,
            add_currency=add_currency,
            monthly=monthly,
            add_type=add_type,
        )

        df = pd.read_sql(query.statement, db.bind)
        if len(df) == 0:
            return df
        df = add_performance_columns(df)
        return df


ga_daily_performance = CRUDGoogleDailyPerformance(GoogleDailyPerformance)
