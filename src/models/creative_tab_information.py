from sqlalchemy import BigInteger, Boolean, Column, Date, ForeignKey, Integer, Sequence
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship
from src.database.base_class import Base


class CreativeTabInformation(Base):
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)
    reference_date = Column(Date, nullable=False)
    ads_generated = Column(Integer, default=0, nullable=False)
    tries_remaining = Column(Integer, default=30, nullable=False)
    purchased_credits_remaining = Column(Integer, default=0, nullable=False)
    counter = Column(Integer, default=0, nullable=False)
    terms_of_service_read = Column(Boolean, default=False, nullable=False)

    shop = relationship("Shop")
