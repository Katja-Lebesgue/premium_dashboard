from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String

from src.database.base_class import Base


class FacebookCampaign(Base):
    shop_id = Column(BigInteger, ForeignKey("shop.id"), primary_key=True)
    account_id = Column(String, primary_key=True)
    campaign_id = Column(String, primary_key=True)
    name = Column(String)
    objective = Column(String)
    status = Column(String)
    created_time = Column(DateTime(timezone=True))
