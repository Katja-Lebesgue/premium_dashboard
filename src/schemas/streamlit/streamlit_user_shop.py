from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from src.database.base_class import Base


class StreamlitUserShopBase(BaseModel):
    streamlit_UserShop_id: int
    shop_id: int


class StreamlitUserShopCreate(StreamlitUserShopBase):
    pass


class StreamlitUserShopUpdate(StreamlitUserShopBase):
    pass
