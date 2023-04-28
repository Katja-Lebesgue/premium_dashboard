from datetime import date, datetime

from sqlalchemy import Float, and_, cast, func, orm
from sqlalchemy.orm import Query, Session

from src import models, schemas
from src.crud.base import CRUDBase
from src.models import ShopifyOrder
from src.utils.common import element_to_list


class CRUDShopifyOrder(CRUDBase[models.ShopifyOrder, schemas.ShopifyOrderCreate, schemas.ShopifyOrderUpdate]):
    def get_sum_of_total_usd_in_period(self, db: orm.Session, shop_id: int, start: datetime, end: datetime) -> int:
        return (
            db.query(func.coalesce(func.sum(models.ShopifyOrder.total_price_usd.cast(Float)), 0))
            .filter(
                and_(
                    models.ShopifyOrder.shop_id == shop_id,
                    models.ShopifyOrder.processed_at >= start,
                    models.ShopifyOrder.processed_at <= end,
                )
            )
            .scalar()
        )

    def get_with_customer_id_set(
        self,
        db: orm.Session,
        shop_id: int,
        offset: int,
        limit: int,
        include_orders_after: datetime | None = None,
    ) -> list[models.ShopifyOrder]:
        query = db.query(models.ShopifyOrder)

        if include_orders_after:
            query = query.filter(
                models.ShopifyOrder.shop_id == shop_id,
                models.ShopifyOrder.customer_id.isnot(None),
                models.ShopifyOrder.created_at >= include_orders_after,
            )
        else:
            query = query.filter(models.ShopifyOrder.shop_id == shop_id, models.ShopifyOrder.customer_id.isnot(None))

        return query.order_by(models.ShopifyOrder.processed_at.asc()).offset(offset).limit(limit).all()

    def get_first_processed_with_customer_id(
        self, db: orm.Session, shop_id: int, customer_id: int
    ) -> models.ShopifyOrder | None:
        return (
            db.query(models.ShopifyOrder)
            .filter(models.ShopifyOrder.customer_id == customer_id, models.ShopifyOrder.shop_id == shop_id)
            .order_by(models.ShopifyOrder.processed_at.asc())
            .first()
        )

    def get_shop_customers_first_order_ids(self, db: orm.Session, shop_id: int):
        return db.execute(
            """select distinct on (customer_id) customer_id, id as first_order_id
                from shopify_order
                where shop_id = :shop_id
                and customer_id is not null
                order by customer_id, processed_at;""",
            {"shop_id": shop_id},
        )

    def query_aov(
        self,
        db: Session,
        shop_id: str | list[str] = None,
        start_date: str = None,
        end_date: str = date.today().strftime("%Y-%m-%d"),
    ) -> Query:

        columns = [
            ShopifyOrder.shop_id,
            func.avg(cast(ShopifyOrder.total_price_usd, Float())).label("aov"),
        ]

        query = db.query(*columns)

        if shop_id is not None:
            shop_id = element_to_list(shop_id)
            query = query.filter(ShopifyOrder.shop_id.in_(shop_id))

        if start_date is not None:
            query = query.filter(
                ShopifyOrder.created_at >= start_date,
                ShopifyOrder.created_at <= end_date,
            )

        query = query.group_by(ShopifyOrder.shop_id)

        query = query.distinct()

        return query


crud_shopify_order = CRUDShopifyOrder(models.ShopifyOrder)
