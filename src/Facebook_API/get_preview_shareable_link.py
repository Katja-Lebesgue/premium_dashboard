import sys

sys.path.append("./.")

import os

import pandas as pd
from dotenv import load_dotenv
from facebook_business.adobjects.ad import Ad
from facebook_business.api import FacebookAdsApi

load_dotenv()


def get_preview_shareable_link(ad_id: str, access_token: str) -> pd.Series:

    # app_id = os.getenv("APP_ID")

    FacebookAdsApi.init(access_token=access_token)

    request = Ad(ad_id)
    request_fb = request.api_get(
        fields=[
            Ad.Field.name,
            Ad.Field.preview_shareable_link,
            Ad.Field.conversion_domain,
        ]
    )

    return request_fb["preview_shareable_link"]
