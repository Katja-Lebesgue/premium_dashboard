from pydantic import BaseModel


class BrandKeywordVolumeBase(BaseModel):
    pass


class BrandKeywordVolumeCreate(BrandKeywordVolumeBase):
    keyword: str
    period: str
    search_volume: int
    competitor_id: int


class BrandKeywordVolumeUpdate(BrandKeywordVolumeBase):
    pass
