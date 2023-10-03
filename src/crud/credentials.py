from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from src import crud, models, schemas
from src.crud.base import CRUDBase
from src.models import enums
from src.models.credentials import Credentials


class CRUDCredentials(CRUDBase[models.Credentials, schemas.CredentialsCreate, schemas.CredentialsUpdate]):
    def get_facebook_access_token_by_shop(
        self,
        db: Session,
        shop_id: int,
    ) -> str:
        subquery = db.query(
            self.model.access_token,
            func.rank()
            .over(
                order_by=self.model.created_date_time.desc(),
                partition_by=self.model.shop_id,
            )
            .label("rnk"),
        ).filter(
            self.model.credentials_provider == "facebook",
            self.model.expired == False,
        )

        subquery = subquery.filter(Credentials.shop_id == shop_id)
        subquery = subquery.subquery()
        access_token = db.query(subquery).filter(subquery.c.rnk == 1).first().access_token

        return access_token


credentials = CRUDCredentials(models.Credentials)
