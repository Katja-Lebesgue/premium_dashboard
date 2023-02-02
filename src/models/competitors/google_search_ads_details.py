from sqlalchemy import BigInteger, Column, ForeignKey, Sequence, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship
from src.database.base_class import Base


class GoogleSearchAdsDetails(Base):
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    keyword_id = Column(BigInteger, ForeignKey("competitor_keywords.id"), nullable=False)
    domain_name = Column(String)
    ad_headline = Column(String)
    ad_description = Column(String)
    ad_landing_page = Column(String)
    ad_url = Column(String)

    keyword = relationship("CompetitorKeywords", back_populates="google_search_ads_details_list")
