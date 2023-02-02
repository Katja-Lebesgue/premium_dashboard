from sqlalchemy import (
    BigInteger,
    Date,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    Sequence,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from src.database.base_class import Base


class LtvBreakdown(Base):
    __table_args__ = (
        UniqueConstraint(
            "shop_id", "breakdown_type", "breakdown_value", "last_day_of_period", "period_length_in_months"
        ),
    )
    id = Column(BigInteger, Sequence("hibernate_sequence"), autoincrement=True, primary_key=True)
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False)
    breakdown_type = Column(String, nullable=False)
    breakdown_value = Column(String, nullable=False)
    last_day_of_period = Column(Date, nullable=False)
    period_length_in_months = Column(Integer, nullable=False)
    ltv = Column(Numeric)
    churn_rate = Column(Numeric)
    retention_rate = Column(Numeric)
    period_type = Column(String, nullable=False)

    shop = relationship("Shop")
