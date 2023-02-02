from sqlalchemy import BigInteger, Boolean, Column, Date, ForeignKey, Numeric, Sequence, SmallInteger, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship
from src.database.base_class import Base


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

    competitor = relationship("Competitor", back_populates="keywords")
    google_search_ads_details_list = relationship(
        "GoogleSearchAdsDetails", back_populates="keyword", lazy="dynamic"
    )

    @property
    def competition(self):
        no_ads = self.google_search_ads_details_list.count()
        if no_ads < 5:
            competition = "low"
        elif no_ads < 10:
            competition = "medium"
        else:
            competition = "high"

        return competition
