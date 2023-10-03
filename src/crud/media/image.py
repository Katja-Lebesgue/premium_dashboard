from datetime import date, datetime, timedelta

import pandas as pd
from sqlalchemy import func, orm
from sqlalchemy.orm import Session

from src import models, schemas
from src.crud.base import CRUDBase
from src.models import *


class CRUDImage(
    CRUDBase[
        models.Image,
        schemas.ImageCreate,
        schemas.ImageUpdate,
    ]
):
    def get_user_uploaded(
        self, db: orm.Session, shop_id: int, limit: int | None = None, days_in_past: int = 2
    ) -> list[models.Image]:
        query = (
            db.query(models.Image)
            .filter(models.Image.shop_id == shop_id, models.Image.source == "user_uploaded")
            .filter(models.Image.last_refreshed >= datetime.utcnow() - timedelta(days=days_in_past))
            .order_by(models.Image.created_at.desc())
        )
        if limit:
            query = query.limit(limit)
        return query.all()

    def get_latest_for_shop(self, db: orm.Session, shop_id: int, limit: int = 5) -> list[models.Image]:
        return (
            db.query(models.Image)
            .filter(models.Image.shop_id == shop_id)
            .order_by(models.Image.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_random_urls(self, db: orm.Session):
        urls = db.query(self.model.url).filter(func.random() < 0.001, self.model.source != "facebook").all()
        return [row.url for row in urls]

    def get_fb_ad_ids_and_image_urls_by_shop(
        self,
        db: Session,
        shop_id: int,
    ):
        fb_ad_image_hash = (
            FacebookAd.creative["object_story_spec"]["link_data"].op("->>")("image_hash").label("image_hash")
        )

        url_query = db.query(
            Image.image_hash,
            Image.url,
            func.rank()
            .over(order_by=Image.created_at.desc(), partition_by=Image.image_hash)
            .label("freshness_rank"),
        ).filter(Image.shop_id == shop_id)
        url_subquery = url_query.subquery()

        fb_ad_query = (
            db.query(FacebookAd.ad_id, FacebookAd.account_id, url_subquery.c.url)
            .join(url_subquery, url_subquery.c.image_hash == fb_ad_image_hash)
            .filter(FacebookAd.shop_id == shop_id, url_subquery.c.freshness_rank == 1)
        )

        return pd.read_sql(fb_ad_query.statement, db.bind).assign(shop_id=shop_id)


image = CRUDImage(models.Image)
