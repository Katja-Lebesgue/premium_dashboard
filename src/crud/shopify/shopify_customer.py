from sqlalchemy import orm
from src import models, schemas

from src.crud.base import CRUDBase


class CRUDShopifyCustomer(
    CRUDBase[models.ShopifyCustomer, schemas.ShopifyCustomerCreate, schemas.ShopifyCustomerUpdate]
):
    def set_and_update_first_order_properties(self, db: orm.Session, shop_id: int):
        db.execute(
            """with shopify_customer_first_order as (select distinct on (customer_id) customer_id,
                                                                       id as order_id,
                                                                       created_at,
                                                                       processed_at
                                      from shopify_order
                                      where shop_id = :shop_id
                                        and customer_id is not null
                                      order by customer_id, processed_at)
                update shopify_customer
                set first_order_id           = shopify_customer_first_order.order_id,
                    first_order_created_at   = shopify_customer_first_order.created_at,
                    first_order_processed_at = shopify_customer_first_order.processed_at
                from shopify_customer_first_order
                where shopify_customer.id = shopify_customer_first_order.customer_id
                and shopify_customer.shop_id = :shop_id;""",
            {"shop_id": shop_id},
        )
        db.commit()

    def set_and_update_last_order_properties(self, db: orm.Session, shop_id: int):
        db.execute(
            """with shopify_customer_last_order as (select distinct on (customer_id) customer_id,
                                                                       id as order_id,
                                                                       created_at,
                                                                       processed_at
                                      from shopify_order
                                      where shop_id = :shop_id
                                        and customer_id is not null
                                      order by customer_id, processed_at desc)
                update shopify_customer
                set last_order_id = shopify_customer_last_order.order_id
                from shopify_customer_last_order
                where shopify_customer.id = shopify_customer_last_order.customer_id
                and shopify_customer.shop_id = :shop_id;""",
            {"shop_id": shop_id},
        )
        db.commit()

    def delete_customer_duplicates(self, db: orm.Session, shop_id: int):
        db.execute(
            """
            with deleted_customer as (
                delete from
                    shopify_customer a
                        using shopify_customer b
                where
                    a.shop_id = b.shop_id
                    and a.email = b.email
                    and a.shop_id = :shop_id
                    and a.id != b.id
                    and a.id < 0
                returning a.id
            )
            delete from customer_first_order_properties
            where shop_id = :shop_id and customer_id in (select id from deleted_customer);
        """,
            {"shop_id": shop_id},
        )
        db.commit()


shopify_customer = CRUDShopifyCustomer(models.ShopifyCustomer)
