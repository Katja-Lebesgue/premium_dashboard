from sqlalchemy.orm import Session

from src.crud.base import CRUDBase
from src.models.facebook.facebook_ad_account import FacebookAdAccount
from src.schemas.facebook.facebook_ad_account import FacebookAdAccountCreate, FacebookAdAccountUpdate


class CRUDFacebookAdAccount(CRUDBase[FacebookAdAccount, FacebookAdAccountCreate, FacebookAdAccountUpdate]):
    def disconnect(self, db: Session, account: FacebookAdAccount):
        self.update(db, db_obj=account, obj_in={"connected": False})

    def disconnect_accounts(self, db: Session, accounts: list[FacebookAdAccount]):
        self.update_multi(db, db_objs=accounts, objs_in=[{"connected": False}] * len(accounts))


fb_ad_account = CRUDFacebookAdAccount(FacebookAdAccount)
