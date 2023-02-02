from typing import TypeVar, Literal
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.crud.base import CRUDBase
from src.database.base_class import Base
from src.models.ltv_breakdown import LtvBreakdown
from src.schemas import LtvBreakdownsCreate, LtvBreakdownsUpdate
from src.services.metrics.order_data.order_data import Breakdown

ModelType = TypeVar("ModelType", bound=Base)


class CRUDLtvBreakdown(CRUDBase[LtvBreakdown, LtvBreakdownsCreate, LtvBreakdownsUpdate]):
    def get_latest_ltv_date(
        self,
        db: Session,
        shop_id: int,
        breakdown: Literal[
            Breakdown.product,
            Breakdown.channel,
            Breakdown.country,
            Breakdown.state,
            Breakdown.discount_title,
            Breakdown.discount_code,
            None,
        ],
    ):
        if breakdown:
            latest_ltv_date = db.query(func.max(self.model.last_day_of_period)).filter_by(
                shop_id=shop_id,
                breakdown_type=breakdown.value,
            )
        else:
            latest_ltv_date = db.query(func.max(self.model.last_day_of_period)).filter_by(
                shop_id=shop_id,
                breakdown_type="total",
            )
        return latest_ltv_date

    def get_latest_ltv_metrics(
        self,
        db: Session,
        shop_id: int,
        breakdown: Literal[
            Breakdown.product,
            Breakdown.channel,
            Breakdown.country,
            Breakdown.state,
            Breakdown.discount_title,
            Breakdown.discount_code,
            None,
        ],
        period_length_in_months: int | None = None,
    ):
        latest_ltv_date = self.get_latest_ltv_date(db, shop_id, breakdown)

        ltv_query = db.query(self.model).filter_by(
            last_day_of_period=latest_ltv_date.scalar_subquery(),  # type: ignore
            shop_id=shop_id,
        )
        if breakdown:
            ltv_query = ltv_query.filter_by(breakdown_type=breakdown.value)
        else:
            ltv_query = ltv_query.filter_by(breakdown_type="total")

        if period_length_in_months:
            ltv_query = ltv_query.filter_by(
                period_length_in_months=period_length_in_months,
            )

        return ltv_query.all()


ltv_breakdown = CRUDLtvBreakdown(LtvBreakdown)
