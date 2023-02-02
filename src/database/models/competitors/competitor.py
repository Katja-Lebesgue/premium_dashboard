from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Sequence, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship
from src.database.base_class import Base
from src.database.models.competitors.competitor_keywords import CompetitorKeywords
from src.database.models.competitors.facebook_ad_from_library import (
    FacebookAdFromLibrary,
)


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
    facebook_page_url = Column(Boolean)
    facebook_page_id = Column(BigInteger)
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)

    shop = relationship("Shop", back_populates="competitors")
    keywords = relationship(
        "CompetitorKeywords", back_populates="competitor", lazy="dynamic"
    )
    brand_keyword_volumes = relationship(
        "BrandKeywordVolume", back_populates="competitor", lazy="dynamic"
    )
    social_media_webpages = relationship(
        "CompetitorSocialMediaWebpages", back_populates="competitor", lazy="dynamic"
    )
    facebook_ads = relationship(
        "FacebookAdFromLibrary", back_populates="competitor", lazy="dynamic"
    )

    @property
    def last_storage_facebook_ads(self) -> list[FacebookAdFromLibrary]:
        last_storage_ad = self.facebook_ads.order_by(
            FacebookAdFromLibrary.storage_date.desc()
        ).first()
        if last_storage_ad is not None:
            return self.facebook_ads.filter(
                FacebookAdFromLibrary.storage_date == last_storage_ad.storage_date
            ).all()
        else:
            return []

    @property
    def last_month_keywords(self) -> list[CompetitorKeywords]:
        last_date_keyword = self.keywords.order_by(
            CompetitorKeywords.date.desc()
        ).first()
        if last_date_keyword is not None:
            return self.keywords.filter(
                CompetitorKeywords.date == last_date_keyword.date
            ).all()
        else:
            return []
