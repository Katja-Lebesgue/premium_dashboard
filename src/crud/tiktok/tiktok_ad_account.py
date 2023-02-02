from sqlalchemy.orm import Session
from src.crud.base import CRUDBase
from src.models.tiktok.tiktok_ad_account import TikTokAdAccount
from src.schemas.tiktok.tiktok_ad_account import TikTokAdAccountCreate, TikTokAdAccountUpdate


class CRUDTikTokAdAccount(CRUDBase[TikTokAdAccount, TikTokAdAccountCreate, TikTokAdAccountUpdate]):
    def disconnect(self, db: Session, account: TikTokAdAccount):
        self.update(db, db_obj=account, obj_in={"connected": False})

    def disconnect_accounts(self, db: Session, accounts: list[TikTokAdAccount]):
        self.update_multi(db, db_objs=accounts, objs_in=[{"connected": False}] * len(accounts))


tt_ad_account = CRUDTikTokAdAccount(TikTokAdAccount)
