from sqlalchemy import BigInteger, Column, Date, ForeignKey, String
from sqlalchemy.orm import relationship

from src.models.google.google_base import GoogleBase


class GoogleCampaign(GoogleBase):

    shop_id = Column(BigInteger, ForeignKey("shop.id"), primary_key=True)
    account_id = Column(BigInteger, primary_key=True)
    campaign_id = Column(BigInteger, primary_key=True)
    name = Column(String)
    type = Column(String)
    strategy = Column(String)
    experiment = Column(String)
    status = Column(String)
    start_date = Column(Date)

    shop = relationship("Shop")
