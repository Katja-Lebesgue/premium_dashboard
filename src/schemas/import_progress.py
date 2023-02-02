from pydantic import BaseModel
from src.enums.common.data_source import DataSource
from src.enums.common.import_type import ImportType

from src.schemas.api_model import APIModel


class ImportProgressBase(BaseModel):
    id: int | None = None
    shop_id: int
    source: DataSource
    num_total_tasks: int
    num_completed_tasks: int
    type: ImportType
    account_id: int


class ImportProgressCreate(ImportProgressBase):
    num_total_tasks: int = 0
    num_completed_tasks: int = 0


class ImportProgressUpdate(ImportProgressBase):
    pass


class ImportProgressApi(APIModel):
    connected: bool
    completed: int
    total: int
    finished: bool


class ImportProgressResponse(APIModel):
    source: ImportProgressApi
