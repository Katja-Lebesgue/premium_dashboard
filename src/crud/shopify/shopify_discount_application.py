from src import models, schemas

from src.crud.base import CRUDBase


class CRUDShopifyDiscountApplication(
    CRUDBase[
        models.ShopifyDiscountApplication,
        schemas.ShopifyDiscountApplicationCreate,
        schemas.ShopifyDiscountApplicationUpdate,
    ]
):
    pass


shopify_discount_application = CRUDShopifyDiscountApplication(models.ShopifyDiscountApplication)
