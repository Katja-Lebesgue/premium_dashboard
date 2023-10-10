from enum import Enum, EnumMeta
from typing import Any


def get_enum_values(enum_: EnumMeta, sort: bool = False) -> list[Any]:
    values = [item.value for item in enum_]
    if sort:
        values.sort()
    return values


def convert_enum_to_its_value(obj: Any) -> Any:
    if isinstance(obj, Enum):
        return obj.value
    return obj
