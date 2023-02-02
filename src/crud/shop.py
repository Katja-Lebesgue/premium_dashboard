from sqlalchemy.orm import Session

from src import models, schemas, crud
from src.models.enums.credentials_provider import CredentialsProvider

from .base import CRUDBase


class CRUDShop(CRUDBase[models.Shop, schemas.ShopCreate, schemas.ShopUpdate]):
    def get_by_name(self, db: Session, name: str) -> models.Shop | None:
        return db.query(models.Shop).filter_by(name=name, rapp_shop=False).first()

    def get_all_active_shops(self, db: Session) -> list[models.Shop]:
        return (
            db.query(models.Shop)
            .filter(
                models.Shop.installed == True,  # noqa: E712
            )
            .all()
        )

    def get_all_active_shops_with_contact_data(self, db: Session) -> list[models.Shop]:
        return (
            db.query(models.Shop)
            .filter(
                models.Shop.installed == True,  # noqa: E712
                models.Shop.contact_email != None,  # noqa: E711
                models.Shop.iana_timezone != None,  # noqa: E711
                models.Shop.weekly_report == True,  # noqa: E712
            )
            .all()
        )

    def get_competitors_import_status_details(self, db: Session, shop: models.Shop) -> dict:
        competitors_all = shop.competitors.all()
        # the actual number is number_of_competitors - 1
        number_of_competitors = len(competitors_all)
        if number_of_competitors <= 1:
            return {"connected": False, "completed": 0, "total": 0, "finished": True}

        completed = 0
        finished = False
        for comp in competitors_all:
            if crud.competitor.is_all_data_imported(db, comp):
                completed += 1
        if completed == number_of_competitors:
            finished = True

        return {
            "connected": True,
            "completed": completed,
            "total": number_of_competitors,
            "finished": finished,
        }

    def uninstall(self, db: Session, shop: models.Shop):
        self.update(db, db_obj=shop, obj_in={"installed": False, "onboarding_completed": False})

        credentials = crud.credentials.get_by_shop_and_provider(db, shop, CredentialsProvider.SHOPIFY)
        if credentials:
            crud.credentials.expire(db, credentials)

        billings = crud.shop_billing.get_all_active(db, shop.id)
        for billing in billings:
            crud.shop_billing.end_billing(db, billing.id)

        fb_accounts = crud.fb_ad_account.get_all_by(db, shop_id=shop.id, connected=True)
        crud.fb_ad_account.disconnect_accounts(db, fb_accounts)

        ga_accounts = crud.ga_ad_account.get_all_by(db, shop_id=shop.id, connected=True)
        crud.ga_ad_account.disconnect_accounts(db, ga_accounts)

        tt_accounts = crud.tt_ad_account.get_all_by(db, shop_id=shop.id, connected=True)
        crud.tt_ad_account.disconnect_accounts(db, tt_accounts)


shop = CRUDShop(models.Shop)
