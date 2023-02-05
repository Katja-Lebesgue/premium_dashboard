from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship
from src.models.google.google_base import GoogleBase

from google.ads.googleads.v11.services.types.google_ads_service import GoogleAdsRow


class GoogleConversionsDetails(GoogleBase):

    shop_id = Column(BigInteger, ForeignKey("shop.id"), primary_key=True)
    google_account_id = Column(BigInteger, primary_key=True)
    conversion_id = Column(BigInteger, primary_key=True)
    conversion_name = Column(String)
    conversion_type = Column(String)
    conversion_category = Column(String)
    conversion_currency = Column(String)
    attribution_model = Column(String)
    click_through_window_days = Column(BigInteger)
    view_through_window_days = Column(BigInteger)

    shop = relationship("Shop")

    @classmethod
    def from_obj(cls, obj: GoogleAdsRow, account_id: int, shop_id: int) -> "GoogleConversionsDetails":
        return cls(
            conversion_id=obj.conversion_action.id,
            conversion_name=obj.conversion_action.name,
            conversion_type=obj.conversion_action.type_.name,
            conversion_category=obj.conversion_action.category.name,
            conversion_currency=obj.conversion_action.value_settings.default_currency_code,
            attribution_model=obj.conversion_action.attribution_model_settings.attribution_model.name,
            click_through_window_days=obj.conversion_action.click_through_lookback_window_days,
            view_through_window_days=obj.conversion_action.view_through_lookback_window_days,
            google_account_id=account_id,
            shop_id=shop_id,
        )
