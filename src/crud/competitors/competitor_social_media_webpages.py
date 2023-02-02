from sqlalchemy.orm import Session
from src.crud.base import CRUDBase
from src.models.competitors.competitor_social_media_webpages import CompetitorSocialMediaWebpages
from src.models.enums.competitor.social_platform import SocialPlatform
from src.schemas.competitors.competitor_social_media_webpages import (
    CompetitorSocialMediaWebpagesUpdate,
    CompetitorSocialMediaWebpagesCreate,
)


class CRUDBCompetitorSocialMediaWebpages(
    CRUDBase[
        CompetitorSocialMediaWebpages,
        CompetitorSocialMediaWebpagesCreate,
        CompetitorSocialMediaWebpagesUpdate,
    ]
):
    def get_by_competitor(self, db: Session, competitor_id: int):
        return (
            db.query(CompetitorSocialMediaWebpages)
            .filter(CompetitorSocialMediaWebpages.competitor_id == competitor_id)
            .all()
        )

    def get_by_competitor_and_platform(self, db: Session, competitor_id: int, platform: SocialPlatform):
        return (
            db.query(CompetitorSocialMediaWebpages)
            .filter(CompetitorSocialMediaWebpages.competitor_id == competitor_id)
            .filter(CompetitorSocialMediaWebpages.platform == platform)
            .all()
        )


competitor_social_media_webpages = CRUDBCompetitorSocialMediaWebpages(CompetitorSocialMediaWebpages)
