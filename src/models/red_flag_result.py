from datetime import datetime

from sqlalchemy import BigInteger, Column, Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from src.database.base_class import Base
from src.enums import AdPlatform


class RedFlagResult(Base):

    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False, primary_key=True)
    date = Column(Date, nullable=False, primary_key=True)
    test = Column(String, nullable=False, primary_key=True)
    source = Column(Enum(AdPlatform, native_enum=False), nullable=False, primary_key=True)
    created_at = Column(DateTime, nullable=False, primary_key=True, default=lambda: datetime.utcnow())
    result = Column(Enum("pass", "error", "fail", native_enum=False))
    comment = Column(Text)

    shop = relationship("Shop", back_populates="red_flag_results")
