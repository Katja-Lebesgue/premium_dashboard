from datetime import date, datetime, timedelta

import pandas as pd
from sqlalchemy import cast, func, orm, select
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
        urls = db.query(models.Image.url).filter(func.random() < 0.001).all()
        return [row.url for row in urls]

    def ping_fb_urls_by_shop(
        self,
        db: Session,
        shop_id: int,
        performance_columns: list[str] = [],
        start_date: date | None = None,
        end_date: date | None = None,
        monthly: bool = False,
    ):
        fb_ad_image_hash = (
            FacebookAd.creative["object_story_spec"]["link_data"].op("->>")("image_hash").label("image_hash")
        )
        url_subquery = (
            db.query(
                Image.image_hash,
                Image.url,
                func.rank()
                .over(order_by=Image.created_at.desc(), partition_by=Image.image_hash)
                .label("freshness_rank"),
            )
            .filter(Image.shop_id == shop_id)
            .subquery()
        )

        fb_ad_query = (
            db.query(FacebookAd.ad_id, FacebookAd.account_id, url_subquery.c.url)
            .join(url_subquery, url_subquery.c.image_hash == fb_ad_image_hash)
            .filter(FacebookAd.shop_id == shop_id, url_subquery.c.freshness_rank == 1)
        )

        if not len(performance_columns):
            df = pd.read_sql(fb_ad_query.statement, db.bind)
        else:
            fb_ad_subquery = fb_ad_query.subquery()
            columns = [FacebookDailyPerformance.ad_id, FacebookDailyPerformance.account_id]
            columns.extend(
                [func.sum(getattr(FacebookDailyPerformance, col)).label(col) for col in performance_columns]
            )

            group_cols = [
                FacebookDailyPerformance.ad_id,
                FacebookDailyPerformance.account_id,
                fb_ad_subquery.c.url,
            ]

            if monthly:
                year_month_col = func.concat(
                    func.extract("year", FacebookDailyPerformance.date_start),
                    "-",
                    func.to_char(func.extract("month", FacebookDailyPerformance.date_start), "fm00"),
                )
                columns.append(year_month_col.label("year_month"))
                group_cols.append(year_month_col)

            filters = [FacebookDailyPerformance.shop_id == shop_id]

            if start_date is not None:
                filters.extend(
                    [
                        FacebookDailyPerformance.date_start >= start_date,
                        FacebookDailyPerformance.date_start <= end_date,
                    ]
                )

            query = (
                db.query(*columns)
                .filter(*filters)
                .join(
                    fb_ad_subquery,
                    (FacebookDailyPerformance.ad_id == fb_ad_subquery.c.ad_id)
                    & (FacebookDailyPerformance.account_id == fb_ad_subquery.c.account_id),
                )
                .add_columns(fb_ad_subquery.c.url)
                .group_by(*group_cols)
            )

            print(str(query))

            df = pd.read_sql(query.statement, db.bind)

        df["shop_id"] = shop_id
        return df


image = CRUDImage(models.Image)
