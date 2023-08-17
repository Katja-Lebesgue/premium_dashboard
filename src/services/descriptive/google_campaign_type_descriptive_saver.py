from datetime import date

import pandas as pd
from sqlalchemy.orm import Session

from src.services.descriptive.descriptive_saver import DescriptiveSaver
from src.abc.descriptive import GoogleCampaignTypeDescriptive
from src import crud


class GoogleCampaignTypeDescriptiveSaver(DescriptiveSaver, GoogleCampaignTypeDescriptive):
    def get_shop_df(self, db: Session, shop_id: int, start_date: date, end_date: date) -> pd.DataFrame:
        return crud.ga_daily_performance.get_performance(
            db=db, shop_id=shop_id, start_date=start_date, end_date=end_date
        )


google_campaign_type_descriptive_saver = GoogleCampaignTypeDescriptiveSaver()
