from pydantic import BaseConfig, BaseModel

from src.utils.string import snake_to_lower_camel_case


class APIModel(BaseModel):
    class Config(BaseConfig):
        allow_population_by_field_name = True
        alias_generator = snake_to_lower_camel_case
