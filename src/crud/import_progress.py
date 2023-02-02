from src import models, schemas
from src.crud.base import CRUDBase


class CRUDImportProgress(
    CRUDBase[models.ImportProgress, schemas.ImportProgressCreate, schemas.ImportProgressUpdate]
):
    pass


import_progress = CRUDImportProgress(models.ImportProgress)
