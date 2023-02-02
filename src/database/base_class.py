import re
from typing import Any

from sqlalchemy import MetaData, inspect
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: Any
    metadata: MetaData
    __name__: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

    @classmethod
    def get_pk_column_names(cls):
        return tuple(key.name for key in inspect(cls).primary_key)

    @property
    def primary_key(self) -> dict[str, Any]:
        return {key: self.__getattribute__(key) for key in self.get_pk_column_names()}  # type: ignore
