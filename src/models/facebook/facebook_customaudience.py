from sqlalchemy import BigInteger, Column, ForeignKey, String

from src.database.base_class import Base


class FacebookCustomaudience(Base):
    shop_id = Column(BigInteger, ForeignKey("shop.id"), primary_key=True)
    account_id = Column(String, primary_key=True)
    customaudience_id = Column(String, primary_key=True)
    subtype = Column(String)
