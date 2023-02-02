from sqlalchemy import BigInteger, Boolean, Column, Date, Enum, ForeignKey, Sequence, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship
from src.database.base_class import Base
from src.models.enums.competitor.social_platform import SocialPlatform


class CompetitorSocialMediaWebpages(Base):
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    platform = Column(Enum(SocialPlatform, native_enum=False), nullable=False)
    url = Column(String, nullable=False)
    last_updated = Column(Date, nullable=True)
    checked = Column(Boolean, nullable=False, default=False)
    competitor_id = Column(BigInteger, ForeignKey("competitor.id"), nullable=False)

    competitor = relationship("Competitor", back_populates="social_media_webpages")
    followers_list = relationship("CompetitorSmFollowers", back_populates="webpage", lazy="dynamic")
