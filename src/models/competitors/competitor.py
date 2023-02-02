from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Sequence, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import foreign, relationship, remote
from sqlalchemy.orm.dynamic import AppenderQuery
from src.database.base_class import Base
from src.models.competitors.competitor_keywords import CompetitorKeywords
from src.models.competitors.facebook_ad_from_library import FacebookAdFromLibrary
from datetime import date, timedelta
from loguru import logger
from functools import cached_property


class Competitor(Base):

    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    website = Column(String)
    competitor_name = Column(String)
    competitor_logo = Column(String)
    app_user = Column(Boolean, default=False)
    facebook_page_url = Column(String)
    facebook_page_id = Column(BigInteger)
    active = Column(Boolean, default=True)
    checked = Column(Boolean, default=False)

    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)
    active = Column(Boolean, default=True)

    shop = relationship("Shop", back_populates="_competitors")
    keywords = relationship("CompetitorKeywords", back_populates="competitor", lazy="dynamic")
    brand_keyword_volumes = relationship("BrandKeywordVolume", back_populates="competitor", lazy="dynamic")
    social_media_webpages = relationship(
        "CompetitorSocialMediaWebpages", back_populates="competitor", lazy="dynamic"
    )
    facebook_ads = relationship(
        FacebookAdFromLibrary,
        primaryjoin=remote(FacebookAdFromLibrary.page_id) == foreign(facebook_page_id),
        lazy="dynamic",
        uselist=True,
        viewonly=True,
    )

    @property
    def is_any_brand_keyword_volume_import_done(self) -> bool:
        if not self.checked:
            return False
        elif self.brand_keyword_volumes.first() is None:
            return False
        return True

    @property
    def is_any_ad_library_import_done(self) -> bool:
        if not self.checked:
            return False
        elif self.facebook_ads.first() is None:
            return False
        return True

    @cached_property
    def all_storage_dates(self) -> list[date]:
        if self.facebook_page_id is None:
            logger.info("There is no facebook page id.")
            all_storage_dates_list = []
        else:
            all_storage_dates_list = (
                self.facebook_ads.distinct(FacebookAdFromLibrary.storage_date).order_by(
                    FacebookAdFromLibrary.storage_date.desc()
                )
            ).all()

        return [d.storage_date for d in all_storage_dates_list]

    @property
    def first_storage_date(self) -> date | None:
        if len(self.all_storage_dates) == 0:
            logger.info("There is no storage dates!")
            return None
        return min(self.all_storage_dates)

    @property
    def before_penultimate_storage_date(self) -> date | None:
        if len(self.all_storage_dates) == 0:
            return None
        if len(self.all_storage_dates) > 2:
            return self.all_storage_dates[2]

    @property
    def penultimate_storage_date(self) -> date | None:
        if len(self.all_storage_dates) == 0:
            return None
        if len(self.all_storage_dates) > 1:
            return self.all_storage_dates[1]

    @property
    def last_storage_date(self) -> date | None:
        if len(self.all_storage_dates) == 0:
            return None
        return max(self.all_storage_dates)

    @property
    def last_storage_facebook_ads(self) -> list[FacebookAdFromLibrary]:
        if self.last_storage_date is not None:
            return self.facebook_ads.filter(
                FacebookAdFromLibrary.storage_date == self.last_storage_date,
            ).all()
        return []

    @property
    def penultimate_storage_facebook_ads(self) -> list[FacebookAdFromLibrary]:
        if self.penultimate_storage_date is not None:
            return self.facebook_ads.filter(
                FacebookAdFromLibrary.storage_date >= self.penultimate_storage_date - timedelta(1),
                FacebookAdFromLibrary.storage_date < self.last_storage_date,
            ).all()
        return []

    @property
    def before_penultimate_storage_facebook_ads(self) -> list[FacebookAdFromLibrary]:
        if self.before_penultimate_storage_date is not None:
            return self.facebook_ads.filter(
                FacebookAdFromLibrary.storage_date >= self.before_penultimate_storage_date - timedelta(1),
                FacebookAdFromLibrary.storage_date < self.penultimate_storage_date,
            ).all()
        return []

    @property
    def last_month_keywords_query(self) -> AppenderQuery | None:
        last_date_keyword = self.keywords.order_by(CompetitorKeywords.date.desc()).first()
        if last_date_keyword is not None:
            return self.keywords.filter(CompetitorKeywords.date == last_date_keyword.date)
        return None
