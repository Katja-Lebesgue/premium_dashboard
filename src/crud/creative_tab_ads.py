from sqlalchemy import orm

from src import models, schemas
from src.crud.base import CRUDBase


class CRUDCreativeTabAds(
    CRUDBase[
        models.CreativeTabAds,
        schemas.CreativeTabAdsCreate,
        schemas.CreativeTabAdsUpdate,
    ]
):
    def get_last_generated_copies(
        self, db: orm.Session, shop_id: int, count: int
    ) -> list[models.CreativeTabAds]:
        return (
            db.query(models.CreativeTabAds)
            .order_by(models.CreativeTabAds.created_at.desc())
            .filter(models.CreativeTabAds.shop_id == shop_id, models.CreativeTabAds.ad_text != "")
            .limit(count)
            .all()
        )


creative_tab_ads = CRUDCreativeTabAds(models.CreativeTabAds)
