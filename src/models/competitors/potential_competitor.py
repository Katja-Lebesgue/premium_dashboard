from sqlalchemy import BigInteger, Column, ForeignKey, Sequence, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship
from src.database.base_class import Base


class PotentialCompetitor(Base):

    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    domain = Column(String)
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)

    shop = relationship("Shop")
