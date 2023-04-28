from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from src.database.base_class import Base


class StreamlitUserBase(BaseModel):
    username: str
    hashed_password: str
    is_superuser: bool


class StreamlitUserCreate(StreamlitUserBase):
    pass


class StreamlitUserUpdate(StreamlitUserBase):
    pass
