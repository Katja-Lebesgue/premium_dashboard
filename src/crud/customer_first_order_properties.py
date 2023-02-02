from sqlalchemy.orm import Session
from src import models, schemas
from src.models import ShopifyOrder
from src.crud.base import CRUDBase
from src.enums import UtmChannel


class CRUDCustomerFirstOrderProperties(
    CRUDBase[
        models.CustomerFirstOrderProperties,
        schemas.CustomerFirstOrderPropertiesCreate,
        schemas.CustomerFirstOrderPropertiesUpdate,
    ]
):
    def get_by_shop_and_customer(
        self, db: Session, shop_id: int, customer_id: int
    ) -> models.CustomerFirstOrderProperties | None:
        return (
            db.query(self.model)
            .filter(
                self.model.shop_id == shop_id,
                self.model.customer_id == customer_id,
            )
            .one_or_none()
        )

    def get_by_shop_customer_and_order(
        self, db: Session, shop_id: int, customer_id: int, order_id: int
    ) -> models.CustomerFirstOrderProperties | None:
        return (
            db.query(self.model)
            .filter(
                self.model.shop_id == shop_id,
                self.model.customer_id == customer_id,
                self.model.order_id == order_id,
            )
            .one_or_none()
        )

    def create_for_shop(self, db: Session, shop: models.Shop):
        db.query(models.CustomerFirstOrderProperties).filter(
            models.CustomerFirstOrderProperties.shop_id == shop.id
        ).delete()

        order_channel_select = str(
            db.query(UtmChannel.derive_channel_sql(ShopifyOrder.utm_parameters)).statement.compile(
                compile_kwargs={"literal_binds": True}
            )
        )
        order_channel = order_channel_select[
            order_channel_select.index("CASE WHEN") : order_channel_select.rindex("END") + 3
        ]
        stmt = f"""
            INSERT INTO customer_first_order_properties (WITH t1 AS
            (select distinct on (customer_id) id
            from shopify_order
            where shop_id = {shop.id}
            and customer_id is not null
            order by customer_id, processed_at),
            t2 AS
            (select
            t1.id,
            array_agg(shopify_line_item.product_id) AS order_product_ids,
            array_agg(shopify_discount_application.code) AS order_discount_codes,
            array_agg(shopify_discount_application.title) AS order_discount_titles
            from t1
            LEFT OUTER JOIN shopify_line_item
            ON shopify_line_item.order_id = t1.id AND shopify_line_item.shop_id = {shop.id}
            LEFT OUTER JOIN shopify_discount_application
            ON shopify_discount_application.order_id = t1.id
            AND shopify_discount_application.shop_id = {shop.id}
            GROUP BY t1.id)
            SELECT
            {shop.id} as shop_id,
            shopify_customer.id as customer_id,
            t2.id as order_id,
            shopify_order.processed_at as order_processed_at,
            t2.order_product_ids,
            shopify_order.utm_parameters as order_utms,
            {order_channel} as order_channel,
            t2.order_discount_codes,
            t2.order_discount_titles,
            shopify_customer.default_country AS customer_default_country_name,
            shopify_customer.default_province AS customer_default_province_name
            FROM t2
            INNER join shopify_order on shopify_order.id = t2.id AND shopify_order.shop_id = {shop.id}
            INNER join shopify_customer
            on shopify_order.customer_id = shopify_customer.id
            and shopify_order.shop_id = shopify_customer.shop_id)
        """
        db.execute(stmt)

        db.commit()


customer_first_order_properties = CRUDCustomerFirstOrderProperties(models.CustomerFirstOrderProperties)
