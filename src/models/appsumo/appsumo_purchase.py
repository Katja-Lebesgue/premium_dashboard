from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relationship
from src.database.base_class import Base
from src.models.enums.appsumo.plan import Plan


class AppsumoPurchase(Base):
    id = Column(BigInteger, primary_key=True)
    invoice_item_uuid = Column(String, nullable=False)
    plan = Column(Enum(Plan), nullable=False)
    user_id = Column(
        BigInteger().with_variant(sqlite.INTEGER, "sqlite"), ForeignKey("user.id"), nullable=False
    )
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="appsumo_purchases")
