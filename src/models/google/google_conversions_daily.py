from sqlalchemy import BigInteger, Column, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship
from src.models.google.google_base import GoogleBase

from google.ads.googleads.v11.services.types.google_ads_service import GoogleAdsRow


class GoogleConversionsDaily(GoogleBase):

    shop_id = Column(BigInteger, ForeignKey("shop.id"), primary_key=True)
    google_account_id = Column(BigInteger, primary_key=True)
    conversion_id = Column(BigInteger, primary_key=True)
    date = Column(Date, primary_key=True)
    category = Column(String)
    count = Column(Numeric)
    value = Column(Numeric)

    shop = relationship("Shop")

    @classmethod
    def from_obj(cls, obj: GoogleAdsRow, account_id: int, shop_id: int) -> "GoogleConversionsDaily":
        return cls(
            conversion_id=int(obj.segments.conversion_action.split("/")[-1]),
            date=obj.segments.date,
            category=obj.segments.conversion_action_category.name,
            count=obj.metrics.conversions,
            value=obj.metrics.conversions_value,
            google_account_id=account_id,
            shop_id=shop_id,
        )
