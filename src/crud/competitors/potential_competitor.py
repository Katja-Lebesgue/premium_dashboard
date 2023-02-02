from src.crud.base import CRUDBase
from src.models.competitors.potential_competitor import PotentialCompetitor
from src.schemas.competitors.potential_competitor import PotentialCompetitorCreate, PotentialCompetitorUpdate


class CRUDPotentialCompetitor(
    CRUDBase[PotentialCompetitor, PotentialCompetitorCreate, PotentialCompetitorUpdate]
):
    pass


potential_competitor = CRUDPotentialCompetitor(PotentialCompetitor)
