import re
from typing import Any

from sqlalchemy import MetaData, inspect
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.ext.hybrid import hybrid_property


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

    @hybrid_property
    def primary_key(self):
        if isinstance(self, Base):
            subject = type(self)
        else:
            subject = self
        return tuple([getattr(self, key.name) for key in inspect(subject).primary_key])

    @classmethod
    @property
    def columns(cls) -> list[str]:
        return list(map(lambda x: x.key, cls.__table__.columns))
