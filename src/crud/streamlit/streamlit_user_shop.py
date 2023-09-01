from typing import List

import pandas as pd
from sqlalchemy.orm import Session

from src.crud.base import CRUDBase
from src.models import Shop
from src.models.streamlit import *
from src.schemas.streamlit import *
from src.utils import element_to_list


class CRUDStreamlitUserShop(CRUDBase[StreamlitUserShop, StreamlitUserShopCreate, StreamlitUserShopUpdate]):
    def add_relationship(self, db: Session, streamlit_user_id: str, shop_id: int) -> None:
        db.add(self.model(streamlit_user_id=streamlit_user_id, shop_id=shop_id))
        db.commit()

    def delete_relationship(self, db: Session, streamlit_user_id: str, shop_id: int) -> None:
        db.query(self.model).filter(
            self.model.streamlit_user_id == streamlit_user_id, self.model.shop_id == shop_id
        ).delete()
        db.commit()

    def get_shops_by_streamlit_user_id(self, db: Session, streamlit_user_id: int) -> pd.DataFrame:
        return (
            db.query(Shop.id, Shop.name)
            .join(self.model, self.model.shop_id == Shop.id)
            .filter(self.model.streamlit_user_id == streamlit_user_id)
        ).all()

    def get_shops_by_streamlit_user_id(self, db: Session, streamlit_user_id: int) -> list[Shop]:
        return (
            db.query(Shop.id, Shop.name)
            .join(self.model, self.model.shop_id == Shop.id)
            .filter(self.model.streamlit_user_id == streamlit_user_id)
            .all()
        )


streamlit_user_shop = CRUDStreamlitUserShop(StreamlitUserShop)
