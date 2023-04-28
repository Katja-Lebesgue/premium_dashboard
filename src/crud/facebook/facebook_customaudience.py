from sqlalchemy.orm import Session

from src.crud.base import CRUDBase
from src.models.facebook.facebook_customaudience import FacebookCustomaudience
from src.schemas.facebook.facebook_customaudience import (
    FacebookCustomaudienceCreate, FacebookCustomaudienceUpdate)


class CRUDFacebookCustomaudience(
    CRUDBase[FacebookCustomaudience, FacebookCustomaudienceCreate, FacebookCustomaudienceUpdate]
):
    def get(
        self, db: Session, shop_id: int, account_id: str, customaudience_id: str
    ) -> FacebookCustomaudience | None:
        return db.query(self.model).get((shop_id, account_id, customaudience_id))


fb_customaudience = CRUDFacebookCustomaudience(FacebookCustomaudience)
