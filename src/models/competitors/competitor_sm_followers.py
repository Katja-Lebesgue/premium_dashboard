from sqlalchemy import BigInteger, Column, Date, ForeignKey
from sqlalchemy.orm import relationship
from src.database.base_class import Base


class CompetitorSmFollowers(Base):
    social_media_webpages_id = Column(
        BigInteger, ForeignKey("competitor_social_media_webpages.id"), primary_key=True
    )
    date = Column(Date, primary_key=True)
    number_followers = Column(BigInteger, nullable=False)

    webpage = relationship("CompetitorSocialMediaWebpages")
