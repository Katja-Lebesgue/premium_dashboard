from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from src.scripts.saving_s3_files.descriptive.descriptive import Descriptive
from src.pingers import ping_target_and_performance


class FacebookTargetDescriptive(Descriptive):
    descriptive_columns = ["target", "gender", "audience"]
    tag = "facebook_target"

    def get_shop_df(self, db: Session, shop_id: int, start_date: date, end_date: date) -> pd.DataFrame:
        return ping_target_and_performance(
            db=db,
            shop_id=shop_id,
            start_date=start_date,
            end_date=end_date,
            enum_to_value=True,
            cast_to_date=False,
        )


facebook_target_descriptive = FacebookTargetDescriptive()
