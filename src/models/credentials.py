from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Enum, ForeignKey, Sequence, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship
from src.database.base_class import Base
from src.models import enums


class Credentials(Base):
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    access_token = Column(String, nullable=False)
    created_date_time = Column(DateTime, default=lambda: datetime.now())
    credentials_provider = Column(Enum(enums.CredentialsProvider, native_enum=False), nullable=False)
    expired = Column(Boolean, default=False)
    refresh_token = Column(String, default=None)
    scope = Column(String, nullable=False)
    expired_date_time = Column(DateTime, default=None)

    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)
    shop = relationship("Shop")

    def expire(self):
        self.expired = True
        self.expired_date_time = datetime.now()
