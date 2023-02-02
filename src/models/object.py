from sqlalchemy import JSON, BigInteger, Column, String
from src.database.base_class import Base


class Object(Base):
    id = Column(BigInteger, primary_key=True)
    object = Column(JSON, nullable=False)
    type = Column(String, nullable=False)
