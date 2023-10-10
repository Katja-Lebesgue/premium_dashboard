from datetime import date, datetime

import pytz
from sqlalchemy import (BigInteger, Boolean, Column, DateTime, ForeignKey,
                        Sequence, SmallInteger, String)
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship, synonym

from src.database.base_class import Base


class FacebookAdAccount(Base):
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)
    facebook_id = Column(String)
    name = Column(String)
    currency = Column(String)
    created_time = Column(DateTime)
    time_zone = Column("timezone_name", String)
    timezone_offset_hours_utc = Column(SmallInteger)
    connected = Column(Boolean, default=False)

    # synonyms
    channel_account_id = synonym("facebook_id")

    shop = relationship("Shop", back_populates="facebook_ad_accounts")

    @property
    def date_now(self) -> date:
        return datetime.now(pytz.timezone(self.time_zone or "UTC")).date()
