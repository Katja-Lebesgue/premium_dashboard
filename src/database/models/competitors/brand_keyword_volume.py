from sqlalchemy import BigInteger, Column, Date, ForeignKey, Sequence, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship
from src.database.base_class import Base


class BrandKeywordVolume(Base):
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    competitor_id = Column(BigInteger, ForeignKey("competitor.id"), nullable=False)
    period = Column(Date)
    keyword = Column(String)
    search_volume = Column(BigInteger)

    competitor = relationship("Competitor", back_populates="brand_keyword_volumes")
