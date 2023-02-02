from sqlalchemy.orm import Session
from src import models, schemas
from src.crud.base import CRUDBase
from src.enums.common.data_source import DataSource


class CRUDImportStatus(CRUDBase[models.ImportStatus, schemas.ImportStatusCreate, schemas.ImportStatusUpdate]):
    def get_one_by_shop_and_data_source(
        self, db: Session, shop_id: int, data_source: DataSource
    ) -> models.ImportStatus | None:
        return (
            db.query(models.ImportStatus)
            .filter(models.ImportStatus.shop_id == shop_id, models.ImportStatus.source == data_source)
            .with_for_update()
            .one_or_none()
        )

    def increase_total_tasks_for_shop_and_data_source(
        self,
        db: Session,
        shop_id: int,
        data_source: DataSource,
        increase_by: int = 1,
    ) -> models.ImportStatus | None:
        import_status = self.get_one_by_shop_and_data_source(db, shop_id, data_source)
        if not import_status:
            return None
        import_status.num_total_tasks += increase_by  # type: ignore
        db.commit()
        return import_status

    def increase_completed_tasks_for_shop_and_data_source(
        self,
        db: Session,
        shop_id: int,
        data_source: DataSource,
        increase_by: int = 1,
    ) -> models.ImportStatus | None:
        import_status = self.get_one_by_shop_and_data_source(db, shop_id, data_source)
        if not import_status:
            return None
        import_status.num_completed_tasks += increase_by  # type: ignore
        db.commit()
        return import_status


import_status = CRUDImportStatus(models.ImportStatus)
