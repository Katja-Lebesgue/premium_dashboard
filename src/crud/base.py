from typing import Any, Generic, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any, commit: bool = False) -> ModelType | None:
        res = db.query(self.model).get(id)
        if commit:
            db.commit()
        return res

    def get_by(self, db: Session, commit: bool = False, **kwargs) -> ModelType | None:
        res = db.query(self.model).filter_by(**kwargs).one_or_none()
        if commit:
            db.commit()
        return res

    def get_multi(
        self, db: Session, *, where=None, order_by=None, skip: int = 0, limit: int = 100, commit: bool = False
    ) -> list[ModelType]:
        query = db.query(self.model)
        if where is not None:
            query = query.filter(where)
        if order_by is not None:
            query = query.order_by(order_by)
        res = query.offset(skip).limit(limit).all()
        if commit:
            db.commit()
        return res

    def get_all(
        self, db: Session, *, where=None, order_by=None, group_by=None, cols=None, commit: bool = False
    ):
        if cols:
            query = db.query(*cols)
        else:
            query = db.query(self.model)

        if where is not None:
            query = query.filter(where)
        if order_by is not None:
            if type(order_by) is list:
                query = query.order_by(*order_by)
            else:
                query = query.order_by(order_by)
        if group_by is not None:
            if type(group_by) is list:
                query = query.group_by(*group_by)
            else:
                query = query.group_by(group_by)

        res = query.all()
        if commit:
            db.commit()
        return res

    def get_all_by(self, db: Session, commit: bool = False, **kwargs) -> list[ModelType]:
        res = db.query(self.model).filter_by(**kwargs).all()
        if commit:
            db.commit()
        return res

    def filter(self, db: Session, *criterion, commit: bool = False) -> list[ModelType]:
        res = db.query(self.model).filter(*criterion).all()
        if commit:
            db.commit()
        return res

    def count(self, db: Session, commit: bool = False):
        res = db.query(self.model).count()
        if commit:
            db.commit()
        return res

    def count_by(self, db: Session, commit: bool = False, **kwargs):
        res = db.query(self.model).filter_by(**kwargs).count()
        if commit:
            db.commit()
        return res

    def create(self, db: Session, *, obj_in: CreateSchemaType, commit: bool = True) -> ModelType:
        # obj_in_data = jsonable_encoder(obj_in)
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        if commit:
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def create_multi(
        self, db: Session, *, objs_in: list[CreateSchemaType], commit: bool = True
    ) -> list[ModelType]:
        db_objs = [self.create(db=db, obj_in=obj_in, commit=False) for obj_in in objs_in]
        if commit:
            db.commit()
            for db_obj in db_objs:
                db.refresh(db_obj)
        return db_objs

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
        commit: bool = True,
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        if commit:
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def update_multi(
        self,
        db: Session,
        *,
        db_objs: list[ModelType],
        objs_in: list[UpdateSchemaType | dict[str, Any]],
        commit: bool = True,
    ) -> list[ModelType]:
        if len(db_objs) != len(objs_in):
            raise Exception("db_objs and objs_in must be of same length.")

        db_objs = [
            self.update(db, db_obj=db_obj, obj_in=obj_in, commit=False)
            for db_obj, obj_in in zip(db_objs, objs_in)
        ]
        if commit:
            db.commit()
            for db_obj in db_objs:
                db.refresh(db_obj)
        return db_objs

    def remove(self, db: Session, *, db_obj: ModelType):
        db.delete(db_obj)
        db.commit()
