from sqlalchemy import BigInteger, Integer, Column, Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from src.database.base_class import Base


class BusinessDaily(Base):
    shop_id = Column(BigInteger, ForeignKey("shop.id"), nullable=False, primary_key=True)
    date = Column(Date, primary_key=True)
    orders = Column(Integer)
    revenue = Column(Numeric)
    first_time_orders = Column(Integer)
    repeat_orders = Column(Integer)
    first_time_revenue = Column(Numeric)
    repeat_revenue = Column(Numeric)
    total_line_items_price = Column(Numeric)
    total_tax = Column(Numeric)
    total_discounts = Column(Numeric)
    total_shipping_price = Column(Numeric)
    aov = Column(Numeric)
    first_time_aov = Column(Numeric)
    repeat_aov = Column(Numeric)
    cancelled_orders = Column(Integer)
    cancelled_revenue = Column(Numeric)
    margin = Column(Numeric)
    cogs = Column(Numeric)

    shop = relationship("Shop")
