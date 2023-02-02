from src import models, schemas

from src.crud.base import CRUDBase


class CRUDShopifyLineItem(
    CRUDBase[models.ShopifyLineItem, schemas.ShopifyLineItemCreate, schemas.ShopifyLineItemUpdate]
):
    pass


shopify_line_item = CRUDShopifyLineItem(models.ShopifyLineItem)
