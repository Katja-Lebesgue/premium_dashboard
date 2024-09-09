from datetime import date, datetime

import pytz
from sqlalchemy import (BigInteger, Boolean, Column, DateTime, ForeignKey,
                        Sequence, SmallInteger, String)
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship

from src.database.base_class import Base


class TikTokAdAccount(Base):
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("user.id"))
    tiktok_id = Column(String)
    name = Column(String)
    currency = Column(String)
    created_time = Column(DateTime)
    time_zone = Column("timezone_name", String)
    timezone_offset_hours_utc = Column(SmallInteger)
    user_connected = Column(Boolean, default=False)
    internally_connected = Column(Boolean, nullable=False, default=False)
    platform_user_id = Column(String)

    shop = relationship("Shop", back_populates="tiktok_ad_accounts")

    @property
    def date_now(self) -> date:
        return datetime.now(pytz.timezone(self.time_zone or "UTC")).date()
