from src import models, schemas
from src.crud.base import CRUDBase


class CRUDCreativeTabInformation(
    CRUDBase[
        models.CreativeTabInformation,
        schemas.CreativeTabInformationCreate,
        schemas.CreativeTabInformationUpdate,
    ]
):
    pass


creative_tab_information = CRUDCreativeTabInformation(models.CreativeTabInformation)
