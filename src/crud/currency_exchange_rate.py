from datetime import date
from src.crud.base import CRUDBase
from sqlalchemy.orm import Session
from src.models import CurrencyExchangeRate
from src.schemas import CurrencyExchangeRateUpdate, CurrencyExchangeRateCreate
from typing import List


class CRUDCurrencyExchangeRate(CRUDBase[CurrencyExchangeRate, CurrencyExchangeRateCreate, CurrencyExchangeRateUpdate]):
    def get_all_in_period_by_currency_code(
        self, db: Session, code: str, begin_date: date = None, end_date: date = None
    ) -> List[CurrencyExchangeRate] | None:
        results = db.query(CurrencyExchangeRate).filter_by(code=code)
        if begin_date:
            results = results.filter(CurrencyExchangeRate.date >= begin_date)
        if end_date:
            results = results.filter(CurrencyExchangeRate.date <= end_date)
        return results.order_by(CurrencyExchangeRate.date.desc()).all()

    def get_by_date_and_currency_code(self, db: Session, code: str, date: date) -> CurrencyExchangeRate | None:
        return db.query(CurrencyExchangeRate).filter_by(code=code, date=date).first()

    def get_last_by_currency_code(self, db: Session, code: str) -> CurrencyExchangeRate | None:
        return db.query(CurrencyExchangeRate).filter_by(code=code).order_by(CurrencyExchangeRate.date.desc()).first()

    def get_by_closest_date_and_code(self, db: Session, code: str, date: date) -> CurrencyExchangeRate | None:
        exact = self.get_by_date_and_currency_code(db, code=code, date=date)
        if exact:
            return exact

        first_after = (
            db.query(CurrencyExchangeRate)
            .filter_by(code=code)
            .filter(CurrencyExchangeRate.date > date)
            .order_by(CurrencyExchangeRate.date.asc())
            .first()
        )

        first_before = (
            db.query(CurrencyExchangeRate)
            .filter_by(code=code)
            .filter(CurrencyExchangeRate.date <= date)
            .order_by(CurrencyExchangeRate.date.desc())
            .first()
        )

        if not first_after:
            return first_before
        if not first_before:
            return first_after

        return first_after if (first_after.date - date).days <= (date - first_before.date).days else first_before

    def query_current_rates(self, db: Session):
        query = (
            db.query(self.model.code, self.model.rate_from_usd)
            .order_by(self.model.code, self.model.date.desc())
            .distinct(self.model.code)
        )
        return query

    def ping_current_rates_dict(self, db: Session) -> dict:
        data = self.query_current_rates(db=db).all()
        return {a.code: a.rate_from_usd for a in data}


crud_currency_exchange_rate = CRUDCurrencyExchangeRate(CurrencyExchangeRate)
