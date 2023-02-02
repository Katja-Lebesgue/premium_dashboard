from datetime import date

from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import literal

from src.crud.base import CRUDBase
from src.models.tiktok.tiktok_ads_insights import TikTokAdsInsights
from src.schemas.tiktok.tiktok_ads_insights import TikTokAdsInsightsCreate, TikTokAdsInsightsUpdate
from src.utils.common import timed_lru_cache
from src.utils.period import PeriodHandlerBase, PeriodTypeBase


class CRUDTikTokAdsInsights(CRUDBase[TikTokAdsInsights, TikTokAdsInsightsCreate, TikTokAdsInsightsUpdate]):
    def get(self, db: Session, shop_id: int, tiktok_account_id: str, date: date) -> TikTokAdsInsights | None:
        return db.query(self.model).get((shop_id, tiktok_account_id, date))

    @timed_lru_cache(
        seconds=5 * 60,
    )
    def get_per_period_metrics(
        self,
        db: Session,
        shop_id: int,
        tiktok_account_id: str,
        period_type: PeriodTypeBase,
        date_first: date,
        date_last: date,
        metrics: tuple[str],
        metrics_mapper: tuple[tuple[str]] = (),
        group_by: tuple[str] = [],
    ):
        """Returns metrics per period.

        Resulting list contains dictionaries with following keys:
            period
            date
            <metric labels>
        """
        metrics = list(metrics)
        group_by = list(group_by)
        metrics_mapper = {k: v for k, v in metrics_mapper}

        where = [
            self.model.shop_id == shop_id,
            self.model.tiktok_account_id == tiktok_account_id,
            self.model.date >= date_first,
            self.model.date <= date_last,
        ]

        if period_type == PeriodTypeBase.all:
            extended_group_by = [literal(1)] + [metrics_mapper.get(g, g) for g in group_by]
            cols = [literal(1).label("period")] + [
                getattr(self.model, metrics_mapper.get(g, g)).label(g) for g in group_by
            ]
            date_func = lambda x: None  # noqa: E731
        else:
            period_handler = PeriodHandlerBase(period_type)
            extended_group_by = [metrics_mapper.get(g, g) for g in group_by] + [
                func.to_char(self.model.date, period_handler.format)
            ]
            cols = [func.to_char(self.model.date, period_handler.format).label("period")] + [
                getattr(self.model, metrics_mapper.get(g, g)).label(g) for g in group_by
            ]
            date_func = period_handler.first_date

        for m in metrics:
            cols.append(func.sum(getattr(self.model, metrics_mapper.get(m, m))).label(m))

        data = self.get_all(db, where=and_(*where), group_by=extended_group_by, cols=cols)
        data = [d._asdict() for d in list(data)]

        for d in data:
            d["date"] = date_func(d["period"])

        return data


tt_ads_insights = CRUDTikTokAdsInsights(TikTokAdsInsights)
