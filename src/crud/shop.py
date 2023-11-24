from datetime import datetime

import pandas as pd
from sqlalchemy import not_, or_
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import false

from src import crud, models, schemas
from src.models.enums.credentials_provider import CredentialsProvider
from src.utils import *

from .base import CRUDBase


class CRUDShop(CRUDBase[models.Shop, schemas.ShopCreate, schemas.ShopUpdate]):
    def ping_all(self, db: Session) -> pd.DataFrame:
        query = db.query(self.model)
        df = read_query_into_df(db=db, query=query)
        return df

    def get_nontest_shops(self, db: Session) -> list[models.Shop]:
        test_shop_phrases = ("anci", "tatjana", "nikola", "test")
        filters = [self.model.name.contains(phrase) for phrase in test_shop_phrases]
        return db.query(self.model).filter(not_(or_(*filters))).all()

    def get_test_shops(self, db: Session) -> list[models.Shop]:
        test_shop_phrases = ("anci", "tatjana", "nikola", "test")
        filters = [self.model.name.contains(phrase) for phrase in test_shop_phrases]
        return db.query(self.model).filter(or_(*filters)).all()


shop = CRUDShop(models.Shop)
