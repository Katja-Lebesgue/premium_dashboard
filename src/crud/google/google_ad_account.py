from sqlalchemy.orm import Session
from src.crud.base import CRUDBase
from src.models.google.google_ad_account import GoogleAdAccount
from src.schemas.google.google_ad_account import GoogleAdAccountCreate, GoogleAdAccountUpdate


class CRUDGoogleAdAccount(CRUDBase[GoogleAdAccount, GoogleAdAccountCreate, GoogleAdAccountUpdate]):
    def disconnect(self, db: Session, account: GoogleAdAccount):
        self.update(db, db_obj=account, obj_in={"connected": False})

    def disconnect_accounts(self, db: Session, accounts: list[GoogleAdAccount]):
        self.update_multi(db, db_objs=accounts, objs_in=[{"connected": False}] * len(accounts))


ga_ad_account = CRUDGoogleAdAccount(GoogleAdAccount)
