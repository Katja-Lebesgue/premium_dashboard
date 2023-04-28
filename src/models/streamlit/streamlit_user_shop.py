from sqlalchemy import Column, ForeignKey, Integer

from src.database.base_class import Base


class StreamlitUserShop(Base):
    id = Column(Integer, primary_key=True)
    streamlit_user_id = Column(Integer, ForeignKey("streamlit_user.id"))
    shop_id = Column(Integer)
