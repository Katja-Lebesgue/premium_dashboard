from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Sequence,
    String,
    cast,
    func,
)
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship
from sqlalchemy.orm.dynamic import AppenderQuery
from src.database.base_class import Base
from src.models.enums import EcommercePlatform


class Shop(Base):
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    name = Column(String)
    onboarded = Column(Boolean, default=False)
    billing_date = Column(Date, default=lambda: datetime.now() + timedelta(days=14))
    rapp_shop = Column(Boolean, default=False)
    currency = Column(String)
    iana_timezone = Column(String)
    location = Column(String)
    contact_email = Column(String)
    weekly_report = Column(Boolean, default=True)
    onboarding_completed = Column(Boolean, default=False)
    shopify_billing_plan = Column(String)
    partner_development = Column(Boolean)
    install_date = Column(DateTime, default=lambda: datetime.now())
    installed = Column(Boolean, default=True)
    contact_name = Column(String)
    shop_name = Column(String)
    mailchimp_subscriber_hash = Column(String)
    owner_id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"), ForeignKey("user.id"), nullable=True
    )
    platform = Column(Enum(EcommercePlatform, native_enum=False), nullable=False)

    tiktok_ad_accounts = relationship("TikTokAdAccount", back_populates="shop", lazy="dynamic")
    tiktok_ads_insights = relationship("TikTokAdsInsights", back_populates="shop", lazy="dynamic")
    facebook_ad_accounts = relationship("FacebookAdAccount", back_populates="shop", lazy="dynamic")
    facebook_ads_insights = relationship("FacebookAdsInsights", back_populates="shop", lazy="dynamic")
    facebook_ad_sets = relationship("FacebookAdset", back_populates="shop")
    facebook_daily_performance = relationship("FacebookDailyPerformance", back_populates="shop")
    google_ad_accounts = relationship("GoogleAdAccount", back_populates="shop", lazy="dynamic")
    google_ads_insights = relationship("GoogleAdsInsights", back_populates="shop", lazy="dynamic")
    red_flag_results = relationship("RedFlagResult", back_populates="shop", lazy="dynamic")
    owner = relationship("User", back_populates="shops")
    business_daily = relationship("BusinessDaily", back_populates="shop")
    _competitors = relationship("Competitor", back_populates="shop", lazy="dynamic")

    @property
    def competitors(self) -> AppenderQuery:
        # filter only active competitors
        return self._competitors.filter_by(active=True)

    orders = relationship("ShopifyOrder", back_populates="shop", lazy="dynamic")
    products = relationship("ShopifyProduct", back_populates="shop", lazy="dynamic")
    customers = relationship("ShopifyCustomer", back_populates="shop", lazy="dynamic")
    billings = relationship("ShopBilling", back_populates="shop", order_by="desc(ShopBilling.updated_at)")

    ad_creative_features = relationship("AdCreativeFeatures", back_populates="shop")

    def __str__(self):
        return f"{self.name} (id {self.id}, user id {self.owner_id})"

    # function for transforming datetimes to datetimes according to shop time zone
    def to_tzone(self, datetime_col: Column[Any]):
        if self.iana_timezone is not None:
            return func.timezone(self.iana_timezone, datetime_col)
        else:
            return datetime_col

    # function for transforming datetimes to dates according to shop time zone
    def to_tzone_date(self, datetime_col: Column[Any]):
        if self.iana_timezone is not None:
            return cast(func.timezone(self.iana_timezone, datetime_col), Date)
        else:
            return cast(datetime_col, Date)
