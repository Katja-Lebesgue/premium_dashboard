from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from src.scripts.saving_s3_files.descriptive.descriptive import Descriptive
from src import crud


class GoogleCampaignTypeDescriptive(Descriptive):
    descriptive_columns = ["campaign_type"]
    tag = "google_campaign_type"

    def get_shop_df(self, db: Session, shop_id: int, start_date: date, end_date: date) -> pd.DataFrame:
        return crud.ga_daily_performance.get_performance(
            db=db, shop_id=shop_id, start_date=start_date, end_date=end_date, add_campaign_type=True
        )


google_campaign_type_descriptive = GoogleCampaignTypeDescriptive()
