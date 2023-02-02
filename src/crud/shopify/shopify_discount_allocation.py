from src import models, schemas

from src.crud.base import CRUDBase


class CRUDShopifyDiscountAllocation(
    CRUDBase[
        models.ShopifyDiscountAllocation,
        schemas.ShopifyDiscountAllocationCreate,
        schemas.ShopifyDiscountAllocationUpdate,
    ]
):
    pass


shopify_discount_allocation = CRUDShopifyDiscountAllocation(models.ShopifyDiscountAllocation)
