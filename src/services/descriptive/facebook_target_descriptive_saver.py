from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from src.services.descriptive.descriptive_saver import DescriptiveSaver
from src.abc.descriptive import FacebookTargetDescriptive
from src.pingers import ping_target_and_performance


class FacebookTargetDescriptiveSaver(DescriptiveSaver, FacebookTargetDescriptive):
    def get_shop_df(self, db: Session, shop_id: int, start_date: date, end_date: date) -> pd.DataFrame:
        return ping_target_and_performance(
            db=db,
            shop_id=shop_id,
            start_date=start_date,
            end_date=end_date,
            enum_to_value=True,
            cast_to_date=False,
        )


facebook_target_descriptive_saver = FacebookTargetDescriptiveSaver()
