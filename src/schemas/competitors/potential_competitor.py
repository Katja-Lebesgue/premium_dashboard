from pydantic import BaseModel


class PotentialCompetitorBase(BaseModel):
    pass


class PotentialCompetitorCreate(PotentialCompetitorBase):
    domain: str
    shop_id: int


class PotentialCompetitorUpdate(PotentialCompetitorBase):
    pass
