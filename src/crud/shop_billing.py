from datetime import datetime

from loguru import logger
from sqlalchemy import orm
from sqlalchemy.sql.expression import true

from src import models, schemas, crud
from src.crud.base import CRUDBase
from src.services import shopify_billing_service
from src.enums.shopify_billing.shopify_billing_plan import ShopifyBillingPlan


class CRUDShopBilling(CRUDBase[models.ShopBilling, schemas.ShopBillingCreate, schemas.ShopBillingUpdate]):
    def get_latest_active(self, db: orm.Session, shop_id: int) -> models.ShopBilling | None:
        return (
            db.query(self.model)
            .filter(self.model.shop_id == shop_id, self.model.active == true())
            .order_by(self.model.updated_at.desc())
            .first()
        )

    def get_all_active(self, db: orm.Session, shop_id: int) -> list[models.ShopBilling]:
        return db.query(self.model).filter(self.model.shop_id == shop_id, self.model.active == true()).all()

    """
        Activates billing for a shop, returns true if successful, false otherwise
    """

    def activate_billing(self, db: orm.Session, id: int) -> bool:
        billing = self.get(db, id)

        if billing:
            self.update(
                db,
                db_obj=billing,
                obj_in=schemas.ShopBillingUpdate(
                    active=True, started_at=datetime.utcnow(), updated_at=datetime.utcnow()
                ),
            )

            logger.info(f"Activated billing [{id}] for shop [{billing.shop_id}]")

            shop = crud.shop.get(db, billing.shop_id)
            if shop and not shop.onboarding_completed:
                crud.shop.update(db, db_obj=shop, obj_in={"onboarding_completed": True})

            return True

        return False

    """
        Ends billing for a shop, returns true if successful, false otherwise
    """

    def end_billing(self, db: orm.Session, id: int) -> bool:
        billing = self.get(db, id)

        if billing:

            if billing.billing_plan == ShopifyBillingPlan.FREE:
                deleted = True
            else:
                deleted = shopify_billing_service.cancel_app_subscription(db, billing.shop_id, id)

            if deleted:
                self.update(
                    db,
                    db_obj=billing,
                    obj_in=schemas.ShopBillingUpdate(
                        active=False, ended_at=datetime.utcnow(), updated_at=datetime.utcnow()
                    ),
                )

                logger.info(f"Ended billing [{id}] for shop [{billing.shop_id}]")

                return True

        return False


shop_billing = CRUDShopBilling(models.ShopBilling)
