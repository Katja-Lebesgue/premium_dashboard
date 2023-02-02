from sqlalchemy import orm

from src import models, schemas

from src.crud.base import CRUDBase
from src.models.enums.shopify_product import ProductStatus


class CRUDShopifyProduct(
    CRUDBase[models.ShopifyProduct, schemas.ShopifyProductCreate, schemas.ShopifyProductUpdate]
):
    def _product_to_representation(self, shop: models.Shop, product: tuple[int, str, str, str, str]):
        return {
            "id": product[0],
            "shop_id": shop.id,
            "url": f"https://{shop.name if shop.name else shop.shop_name}/products/{product[3]}",
            "description": product[2] or "",
            "title": product[1],
            "active": product[4] in [ProductStatus.active, ProductStatus.publish],
        }

    def get_all_product_representations_for_shop(self, db: orm.Session, shop: models.Shop):
        products = (
            db.query(
                models.ShopifyProduct.id,
                models.ShopifyProduct.title,
                models.ShopifyProduct.extracted_description,
                models.ShopifyProduct.handle,
                models.ShopifyProduct.status,
            )
            .filter(models.ShopifyProduct.shop_id == shop.id)
            .all()
        )
        return [self._product_to_representation(shop, product) for product in products]

    def get_all_products_by_title_for_shop(self, db: orm.Session, shop: models.Shop, title: str):
        return (
            db.query(models.ShopifyProduct)
            .filter(models.ShopifyProduct.shop_id == shop.id, models.ShopifyProduct.title == title)
            .all()
        )


shopify_product = CRUDShopifyProduct(models.ShopifyProduct)
