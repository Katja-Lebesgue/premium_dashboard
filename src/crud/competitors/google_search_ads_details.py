from src.crud.base import CRUDBase
from src.models.competitors.google_search_ads_details import GoogleSearchAdsDetails
from src.schemas.competitors.google_search_ads_details import (
    GoogleSearchAdsDetailsCreate,
    GoogleSearchAdsDetailsUpdate,
)


class CRUDGoogleSearchAdsDetails(
    CRUDBase[GoogleSearchAdsDetails, GoogleSearchAdsDetailsCreate, GoogleSearchAdsDetailsUpdate]
):
    pass


google_search_ads_details = CRUDGoogleSearchAdsDetails(GoogleSearchAdsDetails)
