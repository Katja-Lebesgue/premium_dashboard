import os


from loguru import logger
import pandas as pd
from dotenv import load_dotenv
from facebook_business.adobjects.ad import Ad
from facebook_business.api import FacebookAdsApi
from sqlalchemy import func
from sqlalchemy.orm import Session

from src import crud
from src.models import Credentials

load_dotenv()


def get_preview_shareable_link(
    ad_id: str, access_token: str | None, shop_id: int | None = None, db: Session | None = None
) -> pd.Series:
    # app_id = os.getenv("APP_ID")

    if access_token is None and (shop_id is None or db is None):
        raise ValueError("provide either token or shop_id and session.")

    if access_token is None:
        access_token = crud.credentials.get_facebook_access_token_by_shop(db=db, shop_id=shop_id)

    FacebookAdsApi.init(access_token=access_token, api_version="v17.0")

    request = Ad(ad_id)
    try:
        request_fb = request.api_get(
            fields=[
                Ad.Field.name,
                Ad.Field.preview_shareable_link,
                Ad.Field.conversion_domain,
            ]
        )
    except Exception:
        logger.error("Facebook API limit!")
        request_fb = {}

    return request_fb.get("preview_shareable_link", "")
