from src.crud.base import CRUDBase
from src.models.competitors.competitor_keywords import CompetitorKeywords
from src.schemas.competitors.competitor_keywords import CompetitorKeywordsCreate, CompetitorKeywordsUpdate


class CRUDCompetitorKeywords(
    CRUDBase[CompetitorKeywords, CompetitorKeywordsCreate, CompetitorKeywordsUpdate]
):
    pass


competitor_keywords = CRUDCompetitorKeywords(CompetitorKeywords)
