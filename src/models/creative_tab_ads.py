from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Sequence,
    Text,
    func,
)
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.database.base_class import Base
from src.enums.copywriter.creativity_level import CreativityLevel


class CreativeTabAds(Base):
    id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        Sequence("hibernate_sequence"),
        primary_key=True,
        autoincrement=True,
    )
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)
    period = Column(Date, nullable=False)
    ad_text = Column(Text)
    ad_type = Column(Enum(CreativityLevel, native_enum=False))
    specification = Column(JSONB().with_variant(sqlite.JSON, "sqlite"))
    ad_viewed = Column(Boolean, default=False)
    reaction = Column(Integer, default=0)
    created_at = Column(DateTime)

    shop = relationship("Shop")
