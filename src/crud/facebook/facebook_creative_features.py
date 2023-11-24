from datetime import date
import time

from sqlalchemy.orm import Session
from sqlalchemy import func
from loguru import logger

from src.crud.base import CRUDBase
from src.models import FacebookDailyPerformance
from src.models.enums.facebook.creative_features import TextType
from src.models import FacebookCreativeFeatures, Crm
from src.schemas.facebook.facebook_creative_features import (
    FacebookCreativeFeaturesCreate,
    FacebookCreativeFeaturesUpdate,
)
from src.models.enums import Industry


class CRUDFacebookCreativeFeatures(
    CRUDBase[FacebookCreativeFeatures, FacebookCreativeFeaturesCreate, FacebookCreativeFeaturesUpdate]
):
    def get(self, db: Session, shop_id: int, account_id: str, ad_id: str) -> FacebookCreativeFeatures | None:
        return db.query(self.model).get((shop_id, account_id, ad_id))

    def get_text_sample(
        self,
        db: Session,
        text_type: TextType,
        start_date: date,
        end_date: date = date.today(),
        sample_size: int = 10000,
        industry: Industry | None = None,
    ) -> list[FacebookCreativeFeatures]:
        time_filter = FacebookDailyPerformance.date_start.between(start_date, end_date)
        industry_filter = Crm.industry_enum == industry
        # count total number of ads
        # count_filters = [time_filter]
        # if industry is not None:
        #     count_filters.append(industry_filter)
        # t0 = time.time()
        # total_number_of_ads = (
        #     db.query(FacebookDailyPerformance)
        #     .join(Crm, FacebookDailyPerformance.shop_id == Crm.shop_id)
        #     .filter(*count_filters)
        #     .distinct(FacebookDailyPerformance.ad_id, FacebookDailyPerformance.shop_id)
        #     .count()
        # )
        # t1 = time.time()
        # logger.debug(f"time counting = {t1-t0}")
        # logger.debug(total_number_of_ads)

        filters = [
            func.cardinality(getattr(self.model, f"{text_type}")) > 0,
        ]
        query = db.query(
            self.model.shop_id,
            self.model.title,
            self.model.primary,
            self.model.description,
        )

        if start_date is not None:
            query = query.join(
                FacebookDailyPerformance,
                (self.model.ad_id == FacebookDailyPerformance.ad_id)
                & (self.model.account_id == FacebookDailyPerformance.account_id)
                & (self.model.shop_id == FacebookDailyPerformance.shop_id),
            )
            filters.append(FacebookDailyPerformance.date_start.between(start_date, end_date))
        if industry is not None:
            query = query.join(Crm, self.model.shop_id == Crm.shop_id)
            filters.append(Crm.industry_enum == industry)
            query = query.add_column(Crm.industry_enum)

        # sample stochastity
        # query = query.distinct(self.model.ad_id, self.model.shop_id)
        # total_number_of_ads = query.count()
        # logger.debug(total_number_of_ads)
        # sample_ratio = sample_size / total_number_of_ads
        sample_ratio = 0.1
        filters.append(func.random() <= sample_ratio)
        query = query.filter(*filters).limit(sample_size)
        return query.all()


fb_creative_features = CRUDFacebookCreativeFeatures(FacebookCreativeFeatures)
