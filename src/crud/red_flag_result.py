from datetime import date, datetime
from typing import TypeVar

from sqlalchemy.orm import Session
from src.crud.base import CRUDBase
from src.database.base_class import Base
from src.models.red_flag_result import RedFlagResult
from src.schemas.red_flag_result import RedFlagResultCreate, RedFlagResultUpdate

ModelType = TypeVar("ModelType", bound=Base)


class CRUDRedFlagResult(CRUDBase[RedFlagResult, RedFlagResultCreate, RedFlagResultUpdate]):
    def get(
        self, db: Session, shop_id: int, date: date, test: str, source: str, created_at: datetime
    ) -> RedFlagResult | None:
        return db.query(self.model).get((shop_id, date, test, source, created_at))

    def get_by_shop_source_and_date(
        self, db: Session, shop_id: int, source: str, date: date
    ) -> list[RedFlagResult]:
        return self.get_all_by(db, shop_id=shop_id, source=source, date=date)

    def get_latest_date_for_shop(self, db: Session, shop_id: int, source: str):
        return (
            db.query(self.model.date)
            .filter(self.model.shop_id == shop_id, self.model.source == source)
            .order_by(self.model.date.desc())
            .limit(2)
            .all()
        )

    def get_latest_for_date_source_and_test(
        self, db: Session, shop_id: int, date: date, test: str, source: str
    ) -> RedFlagResult | None:
        return (
            db.query(self.model)
            .filter(
                self.model.shop_id == shop_id,
                self.model.source == source,
                self.model.test == test,
                self.model.date == date,
            )
            .order_by(self.model.created_at.desc())
            .first()
        )


red_flag_result = CRUDRedFlagResult(RedFlagResult)
