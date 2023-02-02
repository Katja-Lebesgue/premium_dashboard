from src import models, schemas
from src.crud.base import CRUDBase


class CRUDShopLtvFilter(
    CRUDBase[models.ShopLtvFilter, schemas.ShopLtvFilterCreate, schemas.ShopLtvFilterUpdate]
):
    pass


shop_ltv_filter = CRUDShopLtvFilter(models.ShopLtvFilter)
