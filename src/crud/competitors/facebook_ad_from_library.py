from datetime import timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.crud.base import CRUDBase
from src.models import FacebookAdFromLibrary, Competitor, Shop
from src.schemas.competitors.facebook_ad_from_library import (
    FacebookAdFromLibraryCreate,
    FacebookAdFromLibraryUpdate,
)


class CRUDFacebookAdFromLibrary(
    CRUDBase[FacebookAdFromLibrary, FacebookAdFromLibraryCreate, FacebookAdFromLibraryUpdate]
):
    def _get_new_ads_from_last_storage_facebook_ads(
        self,
        last_storage_ads: list[FacebookAdFromLibrary],
    ) -> list[FacebookAdFromLibrary]:
        last_storage_date = last_storage_ads[0].storage_date
        new_ads = [
            ad
            for ad in last_storage_ads
            if ad.is_active and ad.start_date >= last_storage_date - timedelta(days=14)
        ]
        return new_ads

    def get_new_ads_for_competitor(self, db: Session, competitor: Competitor) -> list[FacebookAdFromLibrary]:
        last_storage_facebook_ads = competitor.last_storage_facebook_ads
        if not last_storage_facebook_ads:
            return []

        return self._get_new_ads_from_last_storage_facebook_ads(last_storage_facebook_ads)

    def get_new_ads_for_shop(self, db: Session, shop: Shop) -> list[FacebookAdFromLibrary]:
        all_shop_ads = db.query(FacebookAdFromLibrary).filter(
            or_(*[FacebookAdFromLibrary.page_id == c.facebook_page_id for c in shop.competitors])
        )
        last_storage_ad = all_shop_ads.order_by(FacebookAdFromLibrary.storage_date.desc()).first()
        if not last_storage_ad:
            return []

        last_storage_ads = all_shop_ads.filter(
            FacebookAdFromLibrary.storage_date == last_storage_ad.storage_date,
        ).all()
        return self._get_new_ads_from_last_storage_facebook_ads(last_storage_ads=last_storage_ads)


fb_ad_from_library = CRUDFacebookAdFromLibrary(FacebookAdFromLibrary)
