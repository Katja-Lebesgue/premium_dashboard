from src.models.insight import Insight
from src.schemas.insight import InsightCreate, InsightUpdate

from .base import CRUDBase


class CRUDInsight(CRUDBase[Insight, InsightCreate, InsightUpdate]):
    pass


insight = CRUDInsight(Insight)
