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
    owner_id = Column(BigInteger().with_variant(sqlite.INTEGER, "sqlite"), ForeignKey("user.id"), nullable=True)
    facebook_ad_accounts = relationship("FacebookAdAccount", back_populates="shop", lazy="dynamic")
    facebook_ads_insights = relationship("FacebookAdsInsights", back_populates="shop", lazy="dynamic")
    facebook_adset_insights = relationship("FacebookAdsetInsights", back_populates="shop", lazy="dynamic")
    facebook_ad_sets = relationship("FacebookAdset", back_populates="shop")
    facebook_daily_performance = relationship("FacebookDailyPerformance", back_populates="shop")
    orders = relationship("ShopifyOrder", back_populates="shop", lazy="dynamic")
    ad_creative_features = relationship("AdCreativeFeatures", back_populates="shop")
    tiktok_ads_insights = relationship("TikTokAdsInsights", back_populates="shop", lazy="dynamic")
    google_ads_insights = relationship("GoogleAdsInsights", back_populates="shop", lazy="dynamic")
    google_ad_accounts = relationship("GoogleAdAccount", back_populates="shop", lazy="dynamic")
    tiktok_ad_accounts = relationship("TikTokAdAccount", back_populates="shop", lazy="dynamic")
