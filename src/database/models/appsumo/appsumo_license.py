from sqlalchemy import BigInteger, Column, Enum, ForeignKey, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship
from src.database.base_class import Base
from src.database.models.enums.appsumo.plan import Plan


class AppsumoLicense(Base):
    product_key = Column(String, primary_key=True, index=True)
    plan = Column(Enum(Plan), nullable=False)
    user_id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"),
        ForeignKey("user.id"),
        nullable=False,
        unique=True,
    )

    user = relationship("User", back_populates="appsumo_license", uselist=False)
