import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import false
from sqlalchemy import or_, not_

from src import crud, models, schemas
from src.models.enums.credentials_provider import CredentialsProvider

from .base import CRUDBase


from datetime import datetime
from sqlalchemy.orm import Session

from src import models, schemas, crud

from .base import CRUDBase


class CRUDShop(CRUDBase[models.Shop, schemas.ShopCreate, schemas.ShopUpdate]):
    def ping_all(self, db: Session) -> pd.DataFrame:
        query = db.query(self.model)
        df = pd.read_sql(query.statement, db.bind)
        return df

    def get_nontest_shops(self, db: Session) -> list[models.Shop]:
        test_shop_phrases = ("anci", "tatjana", "nikola", "test")
        filters = [self.model.name.contains(phrase) for phrase in test_shop_phrases]
        return db.query(self.model).filter(not_(or_(*filters))).all()


shop = CRUDShop(models.Shop)
