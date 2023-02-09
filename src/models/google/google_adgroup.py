from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship
from src.models.google.google_base import GoogleBase


class GoogleAdgroup(GoogleBase):

    shop_id = Column(BigInteger, ForeignKey("shop.id"), primary_key=True)
    account_id = Column(BigInteger, primary_key=True)
    adgroup_id = Column(BigInteger, primary_key=True)
    campaign_id = Column(BigInteger)
    name = Column(String)
    status = Column(String)
    type = Column(String)

    shop = relationship("Shop")
