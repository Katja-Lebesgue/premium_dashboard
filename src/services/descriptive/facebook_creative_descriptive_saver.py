from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from src.models.enums.facebook import BOOLEAN_TEXT_FEATURES
from src.services.descriptive.descriptive_saver import DescriptiveSaver
from src.abc.descriptive import FacebookCreativeDescriptive
from src.pingers import ping_facebook_creative_and_performance


class FacebookCreativeDescriptiveSaver(DescriptiveSaver, FacebookCreativeDescriptive):
    def get_shop_df(self, db: Session, shop_id: int, start_date: date, end_date: date) -> pd.DataFrame:
        return ping_facebook_creative_and_performance(
            db=db,
            shop_id=shop_id,
            start_date=start_date,
            end_date=end_date,
            cast_to_date=False,
            enum_to_value=True,
        )


facebook_creative_descriptive_saver = FacebookCreativeDescriptiveSaver()
