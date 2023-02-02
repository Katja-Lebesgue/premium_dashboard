from src import models, schemas

from src.crud.base import CRUDBase


class CRUDShopifyProductVariant(
    CRUDBase[
        models.ShopifyProductVariant, schemas.ShopifyProductVariantCreate, schemas.ShopifyProductVariantUpdate
    ]
):
    pass


shopify_product_variant = CRUDShopifyProductVariant(models.ShopifyProductVariant)
