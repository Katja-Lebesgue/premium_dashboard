from datetime import datetime

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from src import models, schemas
from src.crud.base import CRUDBase
from src.models import enums
from src.models.credentials import Credentials
from src.utils.help_functions import element_to_list


class CRUDCredentials(CRUDBase[models.Credentials, schemas.CredentialsCreate, schemas.CredentialsUpdate]):
    def get_by_shop_and_provider(
        self, db: Session, shop: models.Shop, provider: enums.CredentialsProvider
    ) -> Credentials | None:
        return (
            db.query(models.Credentials)
            .filter_by(shop=shop, credentials_provider=provider, expired=False)
            .order_by(models.Credentials.created_date_time.desc())
            .first()
        )

    def get_all_expired_by_shop_and_provider(
        self, db: Session, shop: models.Shop, provider: enums.CredentialsProvider
    ) -> list[Credentials]:
        return db.query(models.Credentials).filter_by(shop=shop, credentials_provider=provider, expired=False).all()

    def expire(self, db: Session, credentials: Credentials):
        self.update(db, db_obj=credentials, obj_in=dict(expired=True, expired_date_time=datetime.now()))

    def expire_multi(self, db: Session, credentials: list[Credentials]):
        self.update_multi(
            db,
            db_objs=credentials,
            objs_in=[{"expired": True, "expired_date_time": datetime.now()}] * len(credentials),
        )

    def query_access_token_by_shop_id(
        db: Session,
        shop_id: str | list[str] = None,
    ) -> pd.DataFrame:

        subquery = db.query(
            Credentials.access_token,
            Credentials.shop_id,
            func.rank()
            .over(
                order_by=Credentials.created_date_time.desc(),
                partition_by=Credentials.shop_id,
            )
            .label("rnk"),
        ).filter(
            Credentials.credentials_provider == "FACEBOOK",
            Credentials.expired == False,
        )

        if shop_id is not None:
            shop_id = element_to_list(shop_id)
            subquery = subquery.filter(Credentials.shop_id.in_(shop_id))

        subquery = subquery.subquery()

        query = db.query(subquery).filter(subquery.c.rnk == 1)

        query = query.distinct()

        return query


credentials = CRUDCredentials(models.Credentials)
