from sqlalchemy.dialects import sqlite
from sqlalchemy import Column, Date, String, Float, BigInteger, Sequence, UniqueConstraint

from src.database.base_class import Base


class CurrencyExchangeRate(Base):
    __table_args__ = (
        UniqueConstraint(
            "code",
            "date",
        ),
    )

    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    code = Column(String(length=3), nullable=False, index=True)
    rate_from_usd = Column(Float, nullable=False)
    date = Column(Date, nullable=False)

    def __str__(self):
        return f"{self.date.strftime('%Y-%d-%m')} {self.code}: {self.rate_from_usd}"
