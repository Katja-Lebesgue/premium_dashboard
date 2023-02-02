from sqlalchemy import BigInteger, Column, Enum, ForeignKey, Integer, Sequence, UniqueConstraint
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship
from src.database.base_class import Base
from src.enums.common.data_source import DataSource


class ImportStatus(Base):
    __table_args__ = (
        UniqueConstraint(
            "shop_id",
            "source",
        ),
    )
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)
    source = Column(Enum(DataSource, native_enum=False), nullable=False)
    num_total_tasks = Column(Integer, default=0)
    num_completed_tasks = Column(Integer, default=0)

    shop = relationship("Shop")
