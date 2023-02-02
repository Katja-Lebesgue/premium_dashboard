from typing import Generic, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

NodeT = TypeVar("NodeT")


class Cursors(BaseModel):
    after: str


class Paging(BaseModel):
    cursors: Cursors
    next: str


class FacebookCollection(GenericModel, Generic[NodeT]):
    data: list[NodeT]
    paging: Paging | None
