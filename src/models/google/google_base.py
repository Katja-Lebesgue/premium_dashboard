from src.database.base_class import Base

from google.ads.googleads.v11.services.types.google_ads_service import GoogleAdsRow


class GoogleBase(Base):
    __abstract__ = True

    @classmethod
    def from_obj(cls, obj: GoogleAdsRow, account_id: int, shop_id: int) -> Base:
        raise NotImplementedError
