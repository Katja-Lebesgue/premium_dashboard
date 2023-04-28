from sqlalchemy import Boolean, Column, Integer, LargeBinary, Text

from src.database.base_class import Base


class StreamlitUser(Base):
    id = Column(Integer, primary_key=True)
    username = Column(Text)
    hashed_password = Column(LargeBinary)
    is_superuser = Column(Boolean)
