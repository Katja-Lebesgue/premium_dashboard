from sqlalchemy import Column, String, Integer, Boolean, Text

from src.database.base_class import Base


class StreamlitUser(Base):
    id = Column(Integer, primary_key=True)
    username = Column(Text)
    hashed_password = Column(Text)
    is_superuser = Column(Boolean)
