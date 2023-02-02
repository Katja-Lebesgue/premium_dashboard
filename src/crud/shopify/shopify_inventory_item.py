from src import models, schemas

from src.crud.base import CRUDBase


class CRUDShopifyInventoryItem(
    CRUDBase[
        models.ShopifyInventoryItem, schemas.ShopifyInventoryItemCreate, schemas.ShopifyInventoryItemUpdate
    ]
):
    pass


shopify_inventory_item = CRUDShopifyInventoryItem(models.ShopifyInventoryItem)
