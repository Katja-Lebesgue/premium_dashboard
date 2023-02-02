from pydantic.main import ModelMetaclass


class FieldAccessMetaclass(ModelMetaclass):
    def __getattr__(cls, attr: str):
        return attr
