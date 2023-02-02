from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    ForeignKey,
    Numeric,
    Sequence,
    SmallInteger,
    String,
    func,
)
from sqlalchemy.dialects import sqlite
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from src.database.base_class import Base

COMPETITION_DEFAULT_VALUE = "MEDIUM"


class CompetitorKeywords(Base):
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    competitor_id = Column(BigInteger, ForeignKey("competitor.id"), nullable=False)
    date = Column(Date)
    keyword_text = Column(String)
    avg_monthly_searches = Column(BigInteger)
    used_in_google_ads = Column(Boolean)
    organic_placement = Column(SmallInteger)
    first_organic_position = Column(String)
    keyword_growth = Column(Numeric)
    _competition = Column("competition", String)

    @hybrid_property
    def competition(self):  # type: ignore
        return self._competition if self._competition is not None else COMPETITION_DEFAULT_VALUE

    @competition.setter
    def competition(self, competition):  # type: ignore
        self._competition = competition

    @competition.expression
    def competition(cls):
        return func.coalesce(cls._competition, COMPETITION_DEFAULT_VALUE)

    competitor = relationship("Competitor", back_populates="keywords")
    google_search_ads_details_list = relationship(
        "GoogleSearchAdsDetails", back_populates="keyword", lazy="dynamic"
    )

    @property
    def competing_brands(self):
        _competing_brands = []
        for google_search_ads_details in self.google_search_ads_details_list:
            _competing_brands.append(google_search_ads_details.domain_name)

        return _competing_brands
