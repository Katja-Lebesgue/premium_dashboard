from src.crud.base import CRUDBase
from src.models.competitors.brand_keyword_volume import BrandKeywordVolume
from src.schemas.competitors.brand_keyword_volume import BrandKeywordVolumeCreate, BrandKeywordVolumeUpdate


class CRUDBrandKeywordVolume(
    CRUDBase[BrandKeywordVolume, BrandKeywordVolumeCreate, BrandKeywordVolumeUpdate]
):
    pass


brand_keyword_volume = CRUDBrandKeywordVolume(BrandKeywordVolume)
