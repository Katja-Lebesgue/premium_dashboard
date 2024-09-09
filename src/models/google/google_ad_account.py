from datetime import date, datetime

import pytz
from sqlalchemy import (BigInteger, Boolean, Column, ForeignKey, Sequence,
                        String)
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship, synonym

from src.database.base_class import Base


class GoogleAdAccount(Base):
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("user.id"))
    google_id = Column(BigInteger)
    name = Column(String)
    currency = Column(String)
    time_zone = Column(String)
    user_connected = Column(Boolean, default=False)
    internally_connected = Column(Boolean, default=False, nullable=False)
    login_customer_id = Column(BigInteger)

    shop = relationship("Shop", back_populates="google_ad_accounts")

    # synonyms
    channel_account_id = synonym("google_id")

    @property
    def date_now(self) -> date:
        return datetime.now(pytz.timezone(self.time_zone)).date()
