from datetime import timedelta, date, datetime

from sqlalchemy import func, Date, Integer, orm, and_
from fastapi.encoders import jsonable_encoder

from src import crud
from src.crud.base import CRUDBase
from src.models.competitors.competitor import Competitor
from src.schemas.competitors.competitor import CompetitorCreate, CompetitorUpdate
from src.models import Object, FacebookAdFromLibrary
from src.schemas.competitors.api_responses import ScanInfo, PublishedAdsByDate, CompetitorInfo


class CRUDCompetitor(CRUDBase[Competitor, CompetitorCreate, CompetitorUpdate]):
    def create_with_shop(self, db: orm.Session, *, obj_in: CompetitorCreate, shop_id: int) -> Competitor:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, shop_id=shop_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_ad_library_min_and_max_scan(self, db: orm.Session, competitor: Competitor) -> list[dict]:
        """
        Returning max and min date for ad library import from obejct table:
        - "competitor_id": int,
        - "max_date": date | None,
        - "min_date": str,
        """
        ad_library_import_dates = (
            db.query(
                Object.object.op("->>")("competitor_id").cast(Integer).label("competitor_id"),
                func.max(Object.object.op("->>")("date").cast(Date)).label("max_date"),
                func.min(Object.object.op("->>")("date").cast(Date)).label("min_date"),
            )
            .filter(
                Object.type == "ad_library_import_run",
                Object.object.op("->>")("competitor_id").cast(Integer) == competitor.id,
            )
            .group_by("competitor_id")
        )
        ad_library_import_dates = [d._asdict() for d in ad_library_import_dates.all()]
        return ad_library_import_dates

    def is_any_scan_done(self, db: orm.Session, competitor: Competitor) -> bool:
        """
        Returning bool regard - is any ad library scan done
        """
        ad_library_import = (
            db.query(
                Object.object.op("->>")("competitor_id").cast(Integer).label("competitor_id"),
                Object.object.op("->>")("date").cast(Date).label("date"),
            )
            .filter(
                Object.type == "ad_library_import_run",
                Object.object.op("->>")("competitor_id").cast(Integer) == competitor.id,
            )
            .first()
        )
        if ad_library_import is None:
            return False
        return True

    def is_all_data_imported(self, db: orm.Session, competitor: Competitor):
        brand_and_google_import = competitor.is_any_brand_keyword_volume_import_done
        ad_library_import = competitor.is_any_ad_library_import_done

        if brand_and_google_import and ad_library_import:
            return True
        elif brand_and_google_import and competitor.app_user:
            return True
        elif not brand_and_google_import:
            return False
        else:
            if competitor.facebook_page_id is None:
                return True
            else:
                if not self.is_any_scan_done(db, competitor):
                    shop = crud.shop.get_by(db, id=competitor.shop_id)
                    shop_install_date = shop.install_date.date()
                    # On this date, we started filling the Object table (with scan infos)
                    if shop_install_date < datetime(2022, 9, 20).date():
                        return True
                    else:
                        return False
                else:
                    return True

    def get_competitor_info(self, db: orm.Session, competitor: Competitor) -> CompetitorInfo:

        return CompetitorInfo(
            id=competitor.id,
            competitor_logo=competitor.competitor_logo,
            competitor_name=competitor.competitor_name,
            facebook_page_id=competitor.facebook_page_id,
            facebook_page_url=competitor.facebook_page_url,
            website=competitor.website,
            app_user=competitor.app_user,
            import_done=self.is_all_data_imported(db, competitor),
        )

    def get_scan_info_details(self, db: orm.Session, competitor: Competitor) -> dict:
        """
        Returning scan inforamtion for competitor scraping:
        - "last_scan_date": date | None,
        - "first_scan_date": date | None,
        - "scan_message": str,

        """

        last_storage_date = competitor.last_storage_date
        last_scan_date = last_storage_date
        first_scan_date = competitor.first_storage_date

        min_scan_date = None
        max_scan_date = None
        try:
            if last_storage_date is None:
                ad_library_min_and_max_scan_dates = self.get_ad_library_min_and_max_scan(db, competitor)
                min_scan_date = ad_library_min_and_max_scan_dates[0]["min_date"]
                max_scan_date = ad_library_min_and_max_scan_dates[0]["max_date"]
            elif last_storage_date <= date.today() - timedelta(days=20):
                ad_library_min_and_max_scan_dates = self.get_ad_library_min_and_max_scan(db, competitor)
                min_scan_date = ad_library_min_and_max_scan_dates[0]["min_date"]
                max_scan_date = ad_library_min_and_max_scan_dates[0]["max_date"]

            if max_scan_date is not None:
                first_scan_date = min_scan_date
                last_scan_date = max_scan_date
        except Exception:
            pass

        # set first_scan_date to shop.install_date if there is no storage dates
        # (hardcode first_scan_date for shops that dont have storige dates)
        shop = crud.shop.get_by(db, id=competitor.shop_id)
        shop_install_date = shop.install_date.date()
        if first_scan_date is not None and last_scan_date is not None:
            if last_scan_date > shop_install_date + timedelta(days=14):
                first_scan_date = shop_install_date + timedelta(days=2)

        if competitor.facebook_page_id is None and competitor.checked:
            scan_message = "There is no valid Facebook page for this competitor."
        elif last_scan_date is None and shop_install_date >= datetime(2022, 9, 20).date():
            scan_message = "Import in progress..."
        elif competitor.facebook_page_id is None:
            scan_message = "There is no valid Facebook page for this competitor."
        elif last_storage_date is None:
            scan_message = "This competitor is not running Facebook ads."
        elif last_storage_date <= date.today() - timedelta(days=20):
            scan_message = "This competitor is currently not running Facebook ads."
        else:
            scan_message = "We are scanning your competitor data every two weeks."

        return ScanInfo(
            last_scan_date=last_scan_date,
            first_scan_date=first_scan_date,
            scan_message=scan_message,
        )

    def count_published_ads_by_date(
        self, db: orm.Session, competitor: Competitor, start_date: date
    ) -> list[PublishedAdsByDate]:
        start_date_int = int(start_date.strftime("%s"))
        all_published_facebook_ads = (
            db.query(
                FacebookAdFromLibrary.ad_data.op("->>")("startDate").cast(Integer).label("startDate"),
                func.count(FacebookAdFromLibrary.id.distinct()).label("published_ads"),
            )
            .filter(
                FacebookAdFromLibrary.page_id == competitor.facebook_page_id,
                FacebookAdFromLibrary.ad_data.op("->>")("startDate").cast(Integer).is_not(None),
                FacebookAdFromLibrary.ad_data.op("->>")("startDate").cast(Integer) >= start_date_int,
            )
            .group_by("startDate")
        )
        daily_data = [
            {"date": datetime.utcfromtimestamp(d[0]).date(), "published_ads": d[1]}
            for d in all_published_facebook_ads.all()
        ]

        return daily_data

    def get_unique_fb_ads(self, db: orm.Session, competitor: Competitor) -> FacebookAdFromLibrary:

        subq = (
            db.query(
                FacebookAdFromLibrary.id,
                func.max(FacebookAdFromLibrary.storage_date).label("max_storage_date"),
            )
            .filter(FacebookAdFromLibrary.page_id == competitor.facebook_page_id)
            .group_by(FacebookAdFromLibrary.id)
        ).subquery()

        query = db.query(FacebookAdFromLibrary).join(
            subq,
            and_(
                FacebookAdFromLibrary.id == subq.c.id,
                FacebookAdFromLibrary.storage_date == subq.c.max_storage_date,
            ),
        )
        data = query.order_by(FacebookAdFromLibrary.storage_date.desc()).limit(700).all()

        return data


competitor = CRUDCompetitor(Competitor)
