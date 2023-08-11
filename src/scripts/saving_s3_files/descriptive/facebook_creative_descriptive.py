from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from src.models.enums.facebook import BOOLEAN_TEXT_FEATURES
from src.scripts.saving_s3_files.descriptive.descriptive import Descriptive
from src.pingers import ping_facebook_creative_and_performance


class FacebookCreativeDescriptive(Descriptive):
    descriptive_columns = BOOLEAN_TEXT_FEATURES
    tag = "facebook_creative"

    def get_shop_df(self, db: Session, shop_id: int, start_date: date, end_date: date) -> pd.DataFrame:
        return ping_facebook_creative_and_performance(
            db=db,
            shop_id=shop_id,
            start_date=start_date,
            end_date=end_date,
            cast_to_date=False,
        )


facebook_creative_descriptive = FacebookCreativeDescriptive()
