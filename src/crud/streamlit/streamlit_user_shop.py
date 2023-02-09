from typing import List

from sqlalchemy.orm import Session

from src.crud.base import CRUDBase
from src.models.streamlit import *
from src.schemas.streamlit import *

from src.utils.common import element_to_list


class CRUDStreamlitUserShop(CRUDBase[StreamlitUserShop, StreamlitUserShopCreate, StreamlitUserShopUpdate]):
    def get(self, db: Session, shop_id: int, account_id: str, ad_id: str) -> StreamlitUserShop | None:
        return db.query(self.model).get((shop_id, account_id, ad_id))

    def get_features_by_shop_id(self, db: Session, shop_id: int) -> List[str]:
        ad_creative_features = StreamlitUserShop
        result = db.query(ad_creative_features.feature).filter(ad_creative_features.shop_id == shop_id).distinct()
        return result
