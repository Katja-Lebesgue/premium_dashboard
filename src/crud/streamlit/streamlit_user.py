from typing import List

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import false

from src.crud.base import CRUDBase
from src.models.streamlit import *
from src.schemas.streamlit import *
from src.utils.common import element_to_list
from src.utils.database import row_to_dict


class CRUDStreamlitUser(CRUDBase[StreamlitUser, StreamlitUserCreate, StreamlitUserUpdate]):
    def add_user(
        self, db: Session, username: str, hashed_password: str, is_superuser: bool = False
    ) -> StreamlitUser | None:
        db.add(self.model(username=username, hashed_password=hashed_password, is_superuser=is_superuser))
        db.commit()

    def delete_user(self, db: Session, id: str) -> None:
        db.query(self.model).filter(self.model.id == id).delete()
        db.commit()

    def get_row_by_username(self, db: Session, username: str) -> str:
        row = db.query(StreamlitUser).filter(StreamlitUser.username == username).first()
        return row_to_dict(row)

    def ping_all_subusernames(self, db: Session) -> list[dict]:
        query = db.query(StreamlitUser.id, StreamlitUser.username).filter(StreamlitUser.is_superuser == false())
        df = pd.read_sql(query.statement, db.bind)
        return df

    def update_hashed_password(self, db: Session, id: str, hashed_password: str):
        db.query(self.model).filter(self.model.id == id).update({"hashed_password": hashed_password})
        db.commit()


crud_streamlit_user = CRUDStreamlitUser(StreamlitUser)
