from pydantic import BaseModel
from src.enums.common.data_source import DataSource

from src.schemas.api_model import APIModel


class ImportStatusBase(BaseModel):
    id: int | None = None
    shop_id: int
    source: DataSource
    num_total_tasks: int
    num_completed_tasks: int


class ImportStatusCreate(ImportStatusBase):
    num_total_tasks: int = 0
    num_completed_tasks: int = 0


class ImportStatusUpdate(ImportStatusBase):
    pass


class ImportStatusApi(APIModel):
    connected: bool
    completed: int
    total: int
    finished: bool
