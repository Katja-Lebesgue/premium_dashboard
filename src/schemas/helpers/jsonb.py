from __future__ import annotations

from pydantic import BaseModel


class JSONB(BaseModel):
    __root__: str | int | float | bool | None | dict[str, JSONB] | list[JSONB]
